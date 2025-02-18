from abc import ABC, abstractmethod
from enum import Enum
import time
import threading
from typing import Dict, List, Optional
from pathlib import Path

from context import ContextManager
from indexing.index.generic_index import GenericIndex
from indexing.index.index_list import file_extensions, mapping
from indexing.indexing_operation import IndexingOperation
from indexing.memory import MemoryManager
from provider.provider_instance_registry import (
    ProviderInstanceRegistry, 
    ProviderInstanceRegistryEvent, 
    ProviderInstanceRegistryObserver
)

class IndexRegistryEvent(Enum):
    """Represents events that can occur in the IndexRegistry."""
    ADD = 1    # An index was added
    REMOVE = 2 # An index was removed
    FULL = 3   # An index has reached its capacity

class IndexRegistryObserver(ABC):
    """Abstract observer for receiving index registry updates."""
    
    @abstractmethod
    def notify_registry_update(self, event: IndexRegistryEvent, target: int):
        """Notifies observers about registry updates (add/remove)."""
        pass

    @abstractmethod
    def notify_index_state_update(self, event: IndexRegistryEvent, target: int, index_type: str, position: int):
        """Notifies observers about index state changes (e.g., full index)."""
        pass

class IndexRegistry(ProviderInstanceRegistryObserver):
    """Manages indexes for provider instances, automatically handling their lifecycle."""

    _GLOBAL_INSTANCE = None
    _instance_lock = threading.Lock()  # Class-level lock for singleton instance

    def __init__(self, instance_registry: ProviderInstanceRegistry, memory_manager: MemoryManager, context_manager: ContextManager) -> None:
        """
        Initializes an IndexRegistry instance.
        
        Args:
            instance_registry (ProviderInstanceRegistry): The provider instance registry.
            memory_manager (MemoryManager): Memory manager for handling memory constraints.
            context_manager (ContextManager): Generates unique contexts for indexing operations.
        """
        self._registry: Dict[int, Dict[str, List[GenericIndex]]] = {}
        self._fillable_registry: Dict[int, Dict[str, List[GenericIndex]]] = {}

        self._instance_registry = instance_registry
        self._instance_registry.attach(self)

        self._context_manager = context_manager
        self._memory_manager = memory_manager
        self._observers: List[IndexRegistryObserver] = []
        self._lock = threading.Lock()  # Instance-level lock for thread safety

    @staticmethod
    def instance():
        """Returns the global singleton instance of IndexRegistry."""
        if IndexRegistry._GLOBAL_INSTANCE is None:
            with IndexRegistry._instance_lock:
                if IndexRegistry._GLOBAL_INSTANCE is None:
                    IndexRegistry._GLOBAL_INSTANCE = IndexRegistry(
                        ProviderInstanceRegistry.instance(),
                        MemoryManager.instance(),
                        ContextManager.instance()
                    )
        return IndexRegistry._GLOBAL_INSTANCE

    def attach(self, observer: IndexRegistryObserver):
        """Attaches an observer to receive index registry updates."""
        with self._lock:
            self._observers.append(observer)

    def detach(self, observer: IndexRegistryObserver):
        """Detaches an observer from receiving updates."""
        with self._lock:
            self._observers.remove(observer)

    def _notify_all_registry_update(self, event: IndexRegistryEvent, target: int):
        """Notifies all observers about registry updates."""
        for observer in self._observers:
            observer.notify_registry_update(event, target)

    def _notify_all_index_state_update(self, event: IndexRegistryEvent, target: int, index_type: str, position: int):
        """Notifies all observers about index state updates."""
        for observer in self._observers:
            observer.notify_index_state_update(event, target, index_type, position)

    def notify(self, event: ProviderInstanceRegistryEvent, target: int):
        """Handles provider instance events (addition/removal)."""
        with self._lock:
            if event == ProviderInstanceRegistryEvent.ADD and target not in self._registry:
                self._load_provider_indices(target)
            elif event == ProviderInstanceRegistryEvent.REMOVE:
                self._registry.pop(target, None)
                self._fillable_registry.pop(target, None)

    def get(self, key: int, index_type: str) -> Optional[List[GenericIndex]]:
        """Retrieves the list of indexes for a given provider and index type."""
        with self._lock:
            table = self._registry.get(key)
            if table is None:
                raise ValueError(f"No index table for provider {key} found")
            return table.get(index_type)

    def get_fillable(self, key: int, index_type: str) -> Optional[List[GenericIndex]]:
        """Retrieves the list of fillable indexes for a given provider and index type."""
        with self._lock:
            table = self._fillable_registry.get(key)
            if table is None:
                raise ValueError(f"No fillable index table for provider {key} found")
            return table.get(index_type)
    
    def get_index_types(self, key: int) -> List[str]:
        """
        Retrieves a list of available index types for a given provider instance.
    
        Args:
            key (int): The provider instance ID.
    
        Returns:
            List[str]: A list of available index types for the given provider instance.
    
        Raises:
            ValueError: If the provider instance does not exist.
        """
        table = self._registry.get(key, None)
        if table is None:
            raise ValueError(f"No index table for provider {key} found")
        return list(table.keys())

    def check_instance(self, key: int) -> bool:
        """Checks if an instance exists in the registry."""
        return key in self._registry

    def request_index_creation(self, id: int, ext: str):
        """Requests the creation of a new index for a provider instance."""
        provider_instance = self._instance_registry.get(id)
        if provider_instance is None:
            raise ValueError(f"Provider instance {id} does not exist")

        path = f"{provider_instance.index_path}/{int(time.time() * 1000)}.{ext}"
        extension_to_index = mapping()
        idx_class = extension_to_index[ext]
        new_idx = idx_class(path)

        with self._lock:
            self._registry.setdefault(id, {}).setdefault(ext, []).append(new_idx)

        self._notify_all_registry_update(IndexRegistryEvent.ADD, id)

    def mark_index_as_full(self, target: int, index_type: str, path: str):
        """Marks an index as full and updates observers."""
        with self._lock:
            if target in self._fillable_registry and index_type in self._fillable_registry[target]:
                for idx, index in enumerate(self._fillable_registry[target][index_type]):
                    if index.path == path:
                        del self._fillable_registry[target][index_type][idx]
                        break
                else:
                    raise ValueError(f"Index {path} not found in fillable registry!")

        for idx, index in enumerate(self._registry[target][index_type]):
            if index.path == path:
                self._notify_all_index_state_update(IndexRegistryEvent.FULL, target, index_type, idx)
                return

        raise ValueError(f"Index {path} does not exist in registry!")

    def drain_queue(self, key: int) -> List[IndexingOperation]:
        """
        Drains (empties) the indexing queue for a given provider instance.

        Args:
            key (int): The provider instance ID.
    
        Returns:
            List[IndexingOperation]: A list of all pending indexing operations for the given provider.
        
        Raises:
            ValueError: If the provider instance does not exist.
        """
        provider_instance = self._instance_registry.get(key)
        if provider_instance is not None:
            items: List[IndexingOperation] = []
            while not provider_instance.queue_empty:
                items.append(provider_instance.pop())
            return items
        raise ValueError(f"Provider instance {key} does not exist")

    def _load_provider_indices(self, provider_instance_id: int) -> None:
        """Loads existing indices for a provider instance from disk."""
        provider_instance = self._instance_registry.get(provider_instance_id)
        if provider_instance is None:
            raise ValueError(f"Provider {provider_instance_id} not found in registry!")

        directory = Path(provider_instance.index_path)
        extensions = set(file_extensions())
        files = [f for f in directory.iterdir() if f.is_file() and ".tmp" not in f.suffixes and f.suffix.lstrip('.').lower() in extensions]

        extension_to_index = mapping()

        for f in files:
            ext = f.suffix.lstrip('.').lower()
            idx_class = extension_to_index[ext]
            new_idx = idx_class(f.name)
            context = self._context_manager.generate()
            new_idx.load(context)
            new_idx.release(context)


            index_full = False
            with self._lock:
                self._registry.setdefault(provider_instance_id, {}).setdefault(ext, []).append(new_idx)
                if not self._memory_manager.is_index_full(new_idx.size):
                    self._fillable_registry.setdefault(provider_instance_id, {}).setdefault(ext, []).append(new_idx)
                else:
                    index_full = True

            self._notify_all_registry_update(IndexRegistryEvent.ADD, provider_instance_id)
            if index_full:
                self._notify_all_index_state_update(IndexRegistryEvent.FULL, provider_instance_id, ext, len(self._registry[provider_instance_id][ext]) - 1)
