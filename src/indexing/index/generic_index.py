from abc import ABC, abstractmethod
from collections import deque

class GenericIndex(ABC):
    _NAME: str = "GENERIC"

    def __init__(self, path: str):
        self._document_queue = deque()
        self._path = path

    @property
    def path(self):
        return self._path

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def search(self, **kwargs):
        pass

    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def cluster(self):
        pass

    @classmethod
    def name(cls) -> str:
        return cls._NAME

    @staticmethod
    @abstractmethod
    def create(path: str):
        pass
