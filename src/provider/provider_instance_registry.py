from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Type

from provider.generic_provider import GenericProvider
from globals import DB_SESSION
from schema.connections.provider import Provider

class ProviderInstanceRegistryEvent(Enum):
    ADD = 1
    REMOVE = 2

class ProviderInstanceRegistryObserver(ABC):
    @abstractmethod
    def notify(self, event: ProviderInstanceRegistryEvent, target: int):
        pass

class ProviderInstanceRegistry:
    _GLOBAL_INSTANCE = None

    def __init__(self) -> None:
        self._registry: Dict[int, GenericProvider] = {}
        self._observers: list[ProviderInstanceRegistryObserver] = []

    @staticmethod
    def instance():
        if(ProviderInstanceRegistry._GLOBAL_INSTANCE == None):
            ProviderInstanceRegistry._GLOBAL_INSTANCE = ProviderInstanceRegistry()
        return ProviderInstanceRegistry._GLOBAL_INSTANCE

    def attach(self, observer: ProviderInstanceRegistryObserver):
        self._observers.append(observer);

    def detach(self, observer: ProviderInstanceRegistryObserver):
        self._observers.remove(observer)

    def _notify_all(self, event: ProviderInstanceRegistryEvent, target: int):
        for o in self._observers:
            o.notify(event, target)

    def add(self, key: int, value: GenericProvider) -> bool:
        if key in self._registry:
            return False
        self._registry[key] = value
        self._notify_all(ProviderInstanceRegistryEvent.ADD, key)
        return True

    def remove(self, key: int) -> None:
        if key in self._registry:
            self._registry[key].kill()
            self._registry.pop(key)
            self._notify_all(ProviderInstanceRegistryEvent.REMOVE, key)

    def get(self, key: int) -> None | GenericProvider:
        return self._registry.get(key, None)

    def load_instances(self, cls: Type[GenericProvider]) -> None:
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls.provider_id()).first()
            if provider != None:
                instances = provider.instances
                for instance in instances:
                    self.add(instance.id, cls(instance.id))
