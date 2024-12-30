from typing import Dict, Optional, Type

from provider.generic_provider import GenericProvider
from globals import DB_SESSION
from schema.connections.provider import Provider
from provider.provider_queue import ProviderQueue

class ProviderInstanceRegistry:
    _GLOBAL_INSTANCE = None

    def __init__(self, provider_queue : Optional[ProviderQueue] = None) -> None:
        self._registry: Dict[int, GenericProvider] = {}
        self._provider_queue = provider_queue

    @staticmethod
    def instance():
        if(ProviderInstanceRegistry._GLOBAL_INSTANCE == None):
            ProviderInstanceRegistry._GLOBAL_INSTANCE = ProviderInstanceRegistry(ProviderQueue.instance())
        return ProviderInstanceRegistry._GLOBAL_INSTANCE

    def add(self, key: int, value: GenericProvider) -> bool:
        if key in self._registry:
            return False
        self._registry[key] = value
        if(self._provider_queue):
            self._provider_queue.push(value)
        return True

    def remove(self, key: int) -> None:
        if key in self._registry:
            self._registry[key].kill()
            self._registry.pop(key)

    def get(self, key: int) -> None | GenericProvider:
        return self._registry.get(key, None)

    def load_instances(self, cls: Type[GenericProvider]) -> None:
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls.provider_id()).first()
            if provider != None:
                instances = provider.instances
                for instance in instances:
                    self.add(instance.id, cls(instance.id))
