from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List

from indexing.index.generic_index import GenericIndex
from indexing.indexing_operation import IndexingOperation
from indexing.memory import MemoryManager
from provider.provider_instance_registry import ProviderInstanceRegistry, ProviderInstanceRegistryEvent, ProviderInstanceRegistryObserver

# Responsible for managing the indexes for provider instances
# Loads, creates and deletes them automatically

class IndexRegistryEvent(Enum):
    ADD = 1
    REMOVE = 2

class IndexRegistryObserver(ABC):
    @abstractmethod
    def notify(self, event: IndexRegistryEvent, target: int):
        pass

class IndexRegistry(ProviderInstanceRegistryObserver):
    _GLOBAL_INSTANCE = None

    def __init__(self, instance_registry : ProviderInstanceRegistry, memory_manager: MemoryManager) -> None:
        # For each provider instance id -> list of GenericIndex
        self._registry: Dict[int, List[GenericIndex]]
        self._fillable_registry: Dict[int, List[GenericIndex]]
        self._instance_registry = instance_registry
        self._instance_registry.attach(self)
        self._memory_manager = memory_manager
        self._observers: list[IndexRegistryObserver] = []

    @staticmethod
    def instance():
        if(IndexRegistry._GLOBAL_INSTANCE == None):
            IndexRegistry._GLOBAL_INSTANCE = IndexRegistry(ProviderInstanceRegistry.instance(), MemoryManager.instance())
        return IndexRegistry._GLOBAL_INSTANCE

    def attach(self, observer: IndexRegistryObserver):
        self._observers.append(observer);

    def detach(self, observer: IndexRegistryObserver):
        self._observers.remove(observer)

    def _notify_all(self, event: IndexRegistryEvent, target: int):
        for o in self._observers:
            o.notify(event, target)

    def notify(self, event: ProviderInstanceRegistryEvent, target: int):
        if event == ProviderInstanceRegistryEvent.ADD:
            if target not in self._registry:
                self._load_provider_indices(target)
        elif event == ProviderInstanceRegistryEvent.REMOVE:
            if target in self._registry:
                self._registry.pop(target)

    def get(self, key: int) -> None | List[GenericIndex]:
        return self._registry.get(key, None)
 
    def pop_queue(self, key: int) -> IndexingOperation | None:
        provider_instance = self._instance_registry.get(key)
        if provider_instance != None:
            return provider_instance.pop_nowait()
        raise ValueError(f"Provider instance {key} does not exist")

    def drain_queue(self, key: int) -> List[IndexingOperation]:
        provider_instance = self._instance_registry.get(key)
        if provider_instance != None:
            items: List[IndexingOperation] = []
            while not provider_instance.queue_empty:
                items.append(provider_instance.pop())
            return items
        raise ValueError(f"Provider instance {key} does not exist")

    def queue_empty(self, key: int) -> bool:
        provider_instance = self._instance_registry.get(key)
        if provider_instance != None:
            return provider_instance.queue_empty
        raise ValueError(f"Provider instance {key} does not exist")

    def request_index_creation(self, id : int):
        # TODO: Index creation
        self._notify_all(IndexRegistryEvent.ADD, id)

    # TODO: Implement
    def _load_provider_indices(self, provider_instance: int):
        pass
