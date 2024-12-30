from indexing.index.generic_index import GenericIndex
import faiss
import os

class FaissIndex(GenericIndex):
    _NAME: str = "GENERIC"

    def __init__(self):
        self._faiss: faiss.FaissIndex | None = None
        super()

    def load(self):
        if os.path.exists(self._path):
            index = faiss.read_index(self._path)
        self._faiss
        pass

    def release(self):
        pass

    def search(self, **kwargs):
        pass

    def insert(self):
        pass

    def remove(self):
        pass

    def size(self):
        pass

    def cluster(self):
        pass

    @classmethod
    def name(cls) -> str:
        return cls._NAME

    @staticmethod
    def create(path: str):
        pass
