from threading import Thread, Condition
from typing import Set, Tuple
from context import ContextManager
from indexing.index_registry import IndexRegistry, IndexRegistryEvent, IndexRegistryObserver
from indexing.memory import MemoryManager

class ClusteringQueue(IndexRegistryObserver):
    """
    A thread-safe queue that manages clustering operations for full indices.

    This class listens to index state updates, queues full indices for processing, 
    and processes them in a background thread.

    Attributes:
        _index_registry (IndexRegistry): Manages the available indices.
        _memory_manager (MemoryManager): Manages memory usage.
        _context_manager (ContextManager): Handles execution contexts.
        _status (bool): Indicates whether the queue is running.
        _full_indices (Set[Tuple[int, str, int]]): Stores full index information (provider ID, index type, position).
        _condition (Condition): Used for thread-safe waiting and notification.
        _thread (Thread): Background thread for processing indices.
    """

    _GLOBAL_INSTANCE = None

    def __init__(self, index_registry: IndexRegistry, memory_manager: MemoryManager, context_manager: ContextManager) -> None:
        """
        Initializes the ClusteringQueue with necessary dependencies.

        Args:
            index_registry (IndexRegistry): The index registry instance.
            memory_manager (MemoryManager): The memory manager instance.
            context_manager (ContextManager): The context manager instance.
        """
        self._index_registry = index_registry
        self._index_registry.attach(self)
        self._memory_manager = memory_manager
        self._context_manager = context_manager
        self._status = True
        self._full_indices: Set[Tuple[int, str, int]] = set()
        self._condition = Condition()  # Thread synchronization mechanism
        self._thread = Thread(target=self.run, daemon=True)

    @staticmethod
    def instance():
        """
        Returns a singleton instance of ClusteringQueue.

        Returns:
            ClusteringQueue: The global singleton instance.
        """
        if ClusteringQueue._GLOBAL_INSTANCE is None:
            ClusteringQueue._GLOBAL_INSTANCE = ClusteringQueue(
                IndexRegistry.instance(), MemoryManager.instance(), ContextManager.instance()
            )
        return ClusteringQueue._GLOBAL_INSTANCE

    def notify_registry_update(self, event: IndexRegistryEvent, target: int):
        """
        Handles registry updates, removing full indices associated with deleted provider instances.

        Args:
            event (IndexRegistryEvent): The type of event (ADD, REMOVE, etc.).
            target (int): The provider instance ID.
        """
        if event == IndexRegistryEvent.REMOVE:
            with self._condition:
                self._full_indices = {item for item in self._full_indices if item[0] != target}

    def notify_index_state_update(self, event: IndexRegistryEvent, target: int, index_type: str, position: int):
        """
        Handles index state updates, adding full indices to the processing queue.

        Args:
            event (IndexRegistryEvent): The type of event (FULL).
            target (int): The provider instance ID.
            index_type (str): The type of index.
            position (int): The position of the index in the list.

        Raises:
            ValueError: If the specified index does not exist.
        """
        if event == IndexRegistryEvent.FULL:
            indices_list = self._index_registry.get(target, index_type)
            if indices_list is not None and position < len(indices_list):
                with self._condition:
                    self._full_indices.add((target, index_type, position))
                    self._condition.notify()
            else:
                raise ValueError(f"Index {target}/{index_type}/{position} not found!")

    def start(self):
        """
        Starts the background processing thread.
        """
        self._thread.start()

    def stop(self):
        """
        Stops the clustering queue and notifies the processing thread.
        """
        self._status = False
        with self._condition:
            self._condition.notify_all()

    def run(self):
        """
        Background thread function that waits for and processes full indices.
        """
        while self._status:
            with self._condition:
                while not self._full_indices and self._status:
                    self._condition.wait()  # Wait until notified

            while self._full_indices:
                with self._condition:
                    index_data = self._full_indices.pop()
                self._process_index(index_data)

    def _process_index(self, index_location: Tuple[int, str, int]):
        """
        Processes a full index by clustering and saving it.

        Args:
            index_location (Tuple[int, str, int]): The (provider ID, index type, position) of the index.
        """
        with self._condition:
            index_list = self._index_registry.get(index_location[0], index_location[1])
        if index_list is not None:
            operation_context = self._context_manager.generate()
            index = index_list[index_location[2]]
            index.load(operation_context)
            index.cluster(20)

            # Ensure the index is still valid before saving
            if self._index_registry.check_instance(index_location[0]):
                index.save()
            index.release(operation_context)
