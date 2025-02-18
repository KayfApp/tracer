import threading
from env import (
    INDEX_CLUSTERING_THRESHOLD, MAX_CLUSTERING_MEMORY, MAX_INDEX_SIZE, 
    MAX_INDEXING_MEMORY, MAX_MEMORY
)

class MemoryManager:
    """
    Manages memory allocation for indexing and clustering operations in a multi-threaded environment.
    
    This class ensures thread-safe memory allocation and deallocation, preventing overuse of system resources.
    
    Attributes:
        _GLOBAL_INSTANCE (MemoryManager): Singleton instance.
        _instance_lock (threading.Lock): Lock for singleton instance creation.
    """

    _GLOBAL_INSTANCE = None
    _instance_lock = threading.Lock()  # Class-level lock for thread safety

    def __init__(self, max_index_size: float, index_clustering_threshold: float, 
                 max_memory: float, max_indexing_memory: float, max_clustering_memory: float) -> None:
        """
        Initializes the MemoryManager with memory constraints.

        Args:
            max_index_size (float): Maximum allowed size for an index.
            index_clustering_threshold (float): Threshold for triggering clustering.
            max_memory (float): Total available memory.
            max_indexing_memory (float): Maximum memory allocated for indexing operations.
            max_clustering_memory (float): Maximum memory allocated for clustering operations.
        """
        self._max_index_size = max_index_size
        self._index_clustering_threshold = index_clustering_threshold

        self._max_memory = max_memory
        self._max_indexing_memory = max_indexing_memory
        self._max_clustering_memory = max_clustering_memory

        self._memory_available = max_memory
        self._indexing_memory_available = max_indexing_memory
        self._clustering_memory_available = max_clustering_memory

        self._lock = threading.Lock()  # Lock for memory operations

    @staticmethod
    def instance():
        """
        Returns the global singleton instance of MemoryManager.
        
        Uses double-checked locking to ensure thread-safe instance creation.
        """
        if MemoryManager._GLOBAL_INSTANCE is None:
            with MemoryManager._instance_lock:
                if MemoryManager._GLOBAL_INSTANCE is None:
                    MemoryManager._GLOBAL_INSTANCE = MemoryManager(
                        MAX_INDEX_SIZE, INDEX_CLUSTERING_THRESHOLD, 
                        MAX_MEMORY, MAX_INDEXING_MEMORY, MAX_CLUSTERING_MEMORY
                    )
        return MemoryManager._GLOBAL_INSTANCE

    def use_memory(self, amount: float):
        """
        Allocates general memory.

        Args:
            amount (float): The amount of memory to allocate.

        Raises:
            ValueError: If insufficient memory is available.
        """
        with self._lock:
            if amount > self._memory_available:
                raise ValueError("Not enough general memory available")
            self._memory_available -= amount

    def free_memory(self, amount: float):
        """
        Releases general memory.

        Args:
            amount (float): The amount of memory to release.
        """
        with self._lock:
            self._memory_available += amount

    def use_indexing_memory(self, amount: float):
        """
        Allocates memory for indexing operations.

        Args:
            amount (float): The amount of memory to allocate.

        Raises:
            ValueError: If insufficient indexing or general memory is available.
        """
        with self._lock:
            if amount > self._indexing_memory_available or amount > self._memory_available:
                raise ValueError("Not enough indexing memory available")
            self._indexing_memory_available -= amount
            self._memory_available -= amount

    def free_indexing_memory(self, amount: float):
        """
        Releases memory used for indexing operations.

        Args:
            amount (float): The amount of memory to release.
        """
        with self._lock:
            self._indexing_memory_available += amount
            self._memory_available += amount

    def use_clustering_memory(self, amount: float):
        """
        Allocates memory for clustering operations.

        Args:
            amount (float): The amount of memory to allocate.

        Raises:
            ValueError: If insufficient clustering or general memory is available.
        """
        with self._lock:
            if amount > self._clustering_memory_available or amount > self._memory_available:
                raise ValueError("Not enough clustering memory available")
            self._clustering_memory_available -= amount
            self._memory_available -= amount

    def free_clustering_memory(self, amount: float):
        """
        Releases memory used for clustering operations.

        Args:
            amount (float): The amount of memory to release.
        """
        with self._lock:
            self._clustering_memory_available += amount
            self._memory_available += amount

    @property
    def max_index_size(self) -> float:
        """Returns the maximum allowed index size."""
        return self._max_index_size

    @property
    def index_clustering_threshold(self) -> float:
        """Returns the index clustering threshold."""
        return self._index_clustering_threshold

    def is_index_full(self, size: float) -> bool:
        """
        Checks if an index is considered full based on its size.

        Args:
            size (float): The current size of the index.

        Returns:
            bool: True if the index is full, False otherwise.
        """
        return round(size * self._index_clustering_threshold) >= self._max_index_size
