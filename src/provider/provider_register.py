from typing import Dict, Optional

from provider.generic_provider import GenericProvider
from globals import DB_SESSION
from schema.connections.provider import Provider
from indexing.indexing_queue import IndexingQueue

class ProviderRegister:
    _GLOBAL_INSTANCE = None

    def __init__(self, indexing_queue : Optional[IndexingQueue] = None) -> None:
        self._register: Dict[int, GenericProvider]
        self._indexing_queue = indexing_queue

    @staticmethod
    def instance():
        if(ProviderRegister._GLOBAL_INSTANCE == None):
            ProviderRegister._GLOBAL_INSTANCE = ProviderRegister(IndexingQueue.instance())
        return ProviderRegister._GLOBAL_INSTANCE

    def insert(self, key: int, value: GenericProvider) -> bool:
        if key in self._register:
            return False
        self._register[key] = value
        if(self._indexing_queue):
            self._indexing_queue.push(value)
        return True

    def remove(self, key: int) -> None:
        if key in self._register:
            self._register[key].kill()
            self._register.pop(key)

    def get(self, key: int) -> None | GenericProvider:
        return self._register.get(key, None)

    def load(self, cls) -> None:
        if not issubclass(cls, GenericProvider):
            raise TypeError(f"{cls.__name__} must inherit from BaseProvider")

        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls.provider_id()).first()
            if provider != None:
                instances = provider.instances
                for instance in instances:
                    self.insert(instance.id, cls(instance.id))
