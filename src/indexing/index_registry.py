from typing import Dict

from indexing.index.generic_index import GenericIndex

class IndexRegistry:
    _GLOBAL_INSTANCE = None

    def __init__(self) -> None:
        # key -> index
        self._registry: Dict[str, GenericIndex] = {}
        # attribute -> keys
        self._metadata: Dict[str, set[str]] = {}
        self._provider: Dict[str, set[str]] = {}
        self._in_memory: set[str] = set()

    @staticmethod
    def instance():
        if(IndexRegistry._GLOBAL_INSTANCE == None):
            IndexRegistry._GLOBAL_INSTANCE = IndexRegistry()
        return IndexRegistry._GLOBAL_INSTANCE

    def add(self, key: str, value: GenericIndex, metadata: list[str]) -> None:
        self._registry[key] = value
        for m in metadata:
            self._metadata[m].add(key)

    def remove(self, key: str) -> None:
        self._registry.pop(key)
        for m in self._metadata:
            self._metadata[m].discard(key)

    def get(self, key: str) -> None | GenericIndex:
        if key in self._registry:
            return self._registry[key]
        return None

    def filter(self, metadata: list[str]) -> set[GenericIndex]:
        return set.intersection(*[self._metadata[m] for m in metadata if m in self._metadata])

    def load(self, key: str) -> None:
        self._registry[key].load()
        self._in_memory.add(key)

    def release(self, key: str) -> None:
        self._registry[key].release()
        self._in_memory.remove(key)

    @property
    def in_memory(self) -> set[str]:
        return self._in_memory

    @property
    def available(self):
        return self._registry.keys()
