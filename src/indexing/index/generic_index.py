from abc import ABC, abstractmethod
from collections import deque
from typing import List

class SearchResult:
    def __init__(self, id: int, score: float) -> None:
        self._id = id
        self._score = score

    @property
    def id(self):
        """The id property."""
        return self._id

    @property
    def score(self):
        """The score property."""
        return self._score

class GenericIndex(ABC):
    _NAME: str = "GENERIC"

    def __init__(self, path: str):
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
    def search(self, **kwargs) -> List[SearchResult]:
        pass

    @abstractmethod
    def insert(self, **kwargs):
        pass

    @abstractmethod
    def remove(self, id: int, **kwargs):
        pass

    @abstractmethod
    def size(self):
        pass

    @property
    @abstractmethod
    def is_fillable(self):
        pass

    @abstractmethod
    def cluster(self, **kwargs):
        pass

    @classmethod
    def name(cls) -> str:
        return cls._NAME

    @staticmethod
    @abstractmethod
    def create(path: str, **kwargs):
        pass
