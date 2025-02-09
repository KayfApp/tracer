from env import MAX_CLUSTERING_MEMORY, MAX_INDEXING_MEMORY, MAX_MEMORY
import threading

class MemoryManager:
    _GLOBAL_INSTANCE = None
    _instance_lock = threading.Lock()  # Class-level lock for thread safety

    def __init__(self, max_memory: float, max_indexing_memory: float, max_clustering_memory: float) -> None:
        self._max_memory = max_memory
        self._max_indexing_memory = max_indexing_memory
        self._max_clustering_memory = max_clustering_memory

        self._memory_available = self._max_memory
        self._indexing_memory_available = self._max_indexing_memory
        self._clustering_memory_available = self._max_clustering_memory

        self._lock = threading.Lock()

    @staticmethod
    def instance():
        if MemoryManager._GLOBAL_INSTANCE is None:
            with MemoryManager._instance_lock:  # Use the class-level lock
                if MemoryManager._GLOBAL_INSTANCE is None:
                    MemoryManager._GLOBAL_INSTANCE = MemoryManager(MAX_MEMORY, MAX_INDEXING_MEMORY, MAX_CLUSTERING_MEMORY)
        return MemoryManager._GLOBAL_INSTANCE

    def use_memory(self, amount: float):
        with self._lock:
            if amount <= self._memory_available:
                self._memory_available -= amount
            else:
                raise ValueError("Not enough general memory available")

    def free_memory(self, amount: float):
        with self._lock:
            self._memory_available += amount

    def use_indexing_memory(self, amount: float):
        with self._lock:
            if amount <= self._indexing_memory_available and amount <= self._memory_available:
                self._indexing_memory_available -= amount
                self._memory_available -= amount
            else:
                raise ValueError("Not enough indexing memory available")

    def free_indexing_memory(self, amount: float):
        with self._lock:
            self._indexing_memory_available += amount
            self._memory_available += amount

    def use_clustering_memory(self, amount: float):
        with self._lock:
            if amount <= self._clustering_memory_available and amount <= self._memory_available:
                self._clustering_memory_available -= amount
                self._memory_available -= amount
            else:
                raise ValueError("Not enough clustering memory available")

    def free_clustering_memory(self, amount: float):
        with self._lock:
            self._clustering_memory_available += amount
            self._memory_available += amount
