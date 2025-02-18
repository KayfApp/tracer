from threading import Thread, Condition
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Set, Tuple

from context import ContextManager
from indexing.index.generic_index import GenericIndex
from indexing.index_registry import IndexRegistry, IndexRegistryEvent, IndexRegistryObserver
from indexing.indexing_operation import IndexingOperation, IndexingOperationType
from indexing.memory import MemoryManager
from provider.utils.pipeline import ProcessedDocument

class IndexingQueue(IndexRegistryObserver):
    """
    A thread-safe queue that processes indexing operations asynchronously.
    
    This class listens for changes in the `IndexRegistry` and processes indexing
    operations in the background using a worker thread. It waits for new operations
    or executes pending tasks every 300 seconds.
    
    Attributes:
        _GLOBAL_INSTANCE (IndexingQueue): Singleton instance.
        _index_registry (IndexRegistry): Manages available indexes.
        _memory_manager (MemoryManager): Handles memory allocation for indexes.
        _context_manager (ContextManager): Generates unique contexts.
        _status (bool): Indicates if the queue is running.
        _provider_instances (set): Stores active provider IDs.
        _executor (ThreadPoolExecutor): Manages concurrent processing.
        _condition (Condition): Synchronizes access to the queue.
        _thread (Thread): Background worker thread.
    """

    _GLOBAL_INSTANCE = None  # Singleton instance
    
    def __init__(self, index_registry: IndexRegistry, memory_manager: MemoryManager, context_manager: ContextManager) -> None:
        """
        Initializes the IndexingQueue.

        Args:
            index_registry (IndexRegistry): The index registry instance.
            memory_manager (MemoryManager): Manages memory allocation for indexes.
            context_manager (ContextManager): Generates unique contexts for indexing operations.
        """
        self._index_registry = index_registry
        self._index_registry.attach(self)
        self._memory_manager = memory_manager
        self._context_manager = context_manager
        self._status = True
        self._provider_instances = set()
        self._executor = ThreadPoolExecutor(max_workers=4)  # Enable parallel execution
        self._condition = Condition()  # Synchronization primitive for efficient waiting
        self._thread = Thread(target=self.run, daemon=True)  # Daemon thread runs continuously

    @staticmethod
    def instance():
        """Returns the global singleton instance of IndexingQueue."""
        if IndexingQueue._GLOBAL_INSTANCE is None:
            IndexingQueue._GLOBAL_INSTANCE = IndexingQueue(
                IndexRegistry.instance(), MemoryManager.instance(), ContextManager.instance()
            )
        return IndexingQueue._GLOBAL_INSTANCE

    def notify_registry_update(self, event: IndexRegistryEvent, target: int):
        """
        Handles updates to the IndexRegistry.

        Args:
            event (IndexRegistryEvent): The type of event (ADD or REMOVE).
            target (int): The affected provider instance ID.
        """
        with self._condition:
            if event == IndexRegistryEvent.ADD:
                self._provider_instances.add(target)
            elif event == IndexRegistryEvent.REMOVE:
                self._provider_instances.discard(target)
            self._condition.notify()  # Wake up the run loop

    def notify_index_state_update(self, event: IndexRegistryEvent, target: int, index_type: str, position: int):
        """
        Handles index state updates (not currently used).

        Args:
            event (IndexRegistryEvent): The event type.
            target (int): The target index ID.
            index_type (str): The type of index.
            position (int): Position in the registry.
        """
        return

    def start(self):
        """Starts the background processing thread."""
        self._thread.start()

    def stop(self):
        """Stops the background thread and signals termination."""
        with self._condition:
            self._status = False
            self._condition.notify()  # Wake up the loop to exit

    def run(self):
        """
        Continuously processes indexing operations.

        This method waits for 300 seconds or until a notification arrives, ensuring efficient processing.
        """
        while self._status:
            with self._condition:
                self._condition.wait(timeout=300)  # Wait until timeout or new event

            # Process all provider instances
            for provider_instance_id in list(self._provider_instances):
                operations = self._index_registry.drain_queue(provider_instance_id)
                if operations:
                    self._executor.submit(self._apply_operations, provider_instance_id, operations)

    def _apply_operations(self, provider_instance_id: int, operations: List[IndexingOperation]):
        """
        Processes and applies indexing operations efficiently.

        Args:
            provider_instance_id (int): The ID of the provider instance.
            operations (List[IndexingOperation]): The list of operations to process.
        """
        reduced_operations: Dict[int, List[IndexingOperation]] = {}

        # Optimize operations to reduce unnecessary actions
        for operation in operations:
            doc_id = operation.value.id
            if operation.operation == IndexingOperationType.INSERT:
                if doc_id in reduced_operations and reduced_operations[doc_id] and \
                   reduced_operations[doc_id][-1].operation == IndexingOperationType.DELETE:
                    reduced_operations[doc_id].append(operation)
                else:
                    reduced_operations[doc_id] = [operation]
            else:  # DELETE operation
                if doc_id in reduced_operations and \
                   len(reduced_operations[doc_id]) > 1 and \
                   reduced_operations[doc_id][-1].operation == IndexingOperationType.INSERT and \
                   reduced_operations[doc_id][-2].operation == IndexingOperationType.DELETE:
                    reduced_operations[doc_id] = [operation]
                elif doc_id in reduced_operations and \
                     reduced_operations[doc_id] and \
                     reduced_operations[doc_id][-1].operation == IndexingOperationType.INSERT:
                    reduced_operations.pop(doc_id)
                else:
                    reduced_operations[doc_id] = [operation]

        insert_operations: List[ProcessedDocument] = []
        delete_operations: Set[int] = set()

        # Separate insert and delete operations
        for doc_id, op_list in reduced_operations.items():
            for operation in op_list:
                if operation.operation == IndexingOperationType.INSERT:
                    insert_operations.append(operation.value)
                else:
                    delete_operations.add(doc_id)

        reserved_indices: List[Tuple[GenericIndex, Set[int]]] = []

        if not self._index_registry.check_instance(provider_instance_id):
            return

        # Retrieve all relevant indexes
        index_types = self._index_registry.get_index_types(provider_instance_id)
        if index_types is None:
            return

        for index_type in index_types:
            index_list = self._index_registry.get(provider_instance_id, index_type)
            if index_list is None:
                return
            for index in index_list:
                id_intersection = index.id_intersection(delete_operations)
                if id_intersection:
                    reserved_indices.append((index, id_intersection))

        # Apply delete and insert operations with memory constraints
        insertion_begin = 0
        for index, ids in reserved_indices:
            operation_context = self._context_manager.generate()
            index.load(operation_context)
            index.remove(list(ids))
            capacity = index.capacity(self._memory_manager.max_index_size)
            index.insert(insert_operations[insertion_begin:insertion_begin + capacity])
            insertion_begin += capacity
            if self._index_registry.check_instance(provider_instance_id):
                index.save()
            else:
                index.release(operation_context)
                return
            index.release(operation_context)

        # TODO: fill the rest of indices if not all insertion items have been added
