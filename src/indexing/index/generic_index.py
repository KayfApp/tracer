
from abc import ABC, abstractmethod
from multiprocessing import Process
from typing import List, Optional, Set
from context import Context
from provider.utils.pipeline import ProcessedDocument
from schema.document.sub_document import SubDocument
from threading import Lock

class SearchResult:
    """
    Represents a search result with an associated ID and score.
    """

    def __init__(self, id: int, score: float) -> None:
        self._id = id
        self._score = score

    @property
    def id(self) -> int:
        """Returns the ID of the search result."""
        return self._id

    @property
    def score(self) -> float:
        """Returns the score of the search result."""
        return self._score


class GenericIndex(ABC):
    """
    Abstract base class for generic indexing structures.
    """

    _NAME: str = "GENERIC"
    _EXT: str = "generic"
    _lock = Lock()  # Lock for thread safety

    def __init__(self, path: str, **kwargs) -> None:
        self._path = path

    @abstractmethod
    def load(self, context: Optional[Context] = None) -> None:
        """
        Load the index data from the specified path.

        Args:
            context (Optional[Context]): Context for loading the index.
        """
        pass

    @abstractmethod
    def release(self, context: Optional[Context] = None) -> None:
        """
        Release resources associated with the index.

        Args:
            context (Optional[Context]): Context for releasing the index.
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int) -> List[SearchResult]:
        """
        Search for documents matching the query.

        Args:
            query (str): The search query.
            k (int): The number of top results to return.

        Returns:
            List[SearchResult]: A list of search results.
        """
        pass

    @abstractmethod
    def has_id(self, id: int) -> bool:
        """
        Check if an ID exists in the index.

        Args:
            id (int): The ID to check.

        Returns:
            bool: True if the ID exists, False otherwise.
        """
        pass

    @abstractmethod
    def id_intersection(self, ids: Set[int]) -> Set[int]:
        """
        Find the intersection of IDs in the index.

        Args:
            ids (Set[int]): A set of IDs to intersect.

        Returns:
            Set[int]: A set of IDs that exist in both the index and the provided set.
        """
        pass

    @abstractmethod
    def insert(self, documents: List[ProcessedDocument]) -> None:
        """
        Insert documents into the index.

        **Note**: This method does not handle existing IDs. 
        Inserting documents with IDs that already exist may cause undefined behavior,
        such as duplicates or data corruption.

        Args:
            documents (List[SubDocument]): The list of documents to insert.
        """
        pass

    @abstractmethod
    def remove(self, ids: List[int]) -> None:
        """
        Remove documents from the index by their IDs.

        Args:
            ids (List[int]): The IDs of the documents to remove.
        """
        pass

    @abstractmethod
    def save(self, path: Optional[str] = None) -> None:
        """
        Save the index data to the specified path.

        Args:
            path (Optional[str]): The path to save the index. 
                                  If None, save to the original path.
        """
        pass

    @property
    @abstractmethod
    def size(self) -> float:
        """
        Returns the current size of the index.

        Returns:
            float: The size of the index.
        """
        pass

    @property
    @abstractmethod
    def max_doc_size(self) -> float:
        """
        Returns the maximum document size allowed in the index.

        Returns:
            float: The maximum document size.
        """
        pass

    @abstractmethod
    def capacity(self, max_index_size: float) -> int:
        """
        Calculate the index's capacity based on the maximum index size.

        Args:
            max_index_size (float): The maximum size allowed for the index.

        Returns:
            int: The calculated capacity of the index.
        """
        pass

    @abstractmethod
    def cluster(self, cluster_n: int) -> None:
        """
        Cluster the index data into groups.

        Args:
            cluster_n (int): The number of clusters to create.
        """
        pass

    @property
    def path(self) -> str:
        """Returns the path of the index."""
        return self._path

    @classmethod
    def name(cls) -> str:
        """Returns the name of the index class."""
        return cls._NAME

    @classmethod
    def extension(cls) -> str:
        """Returns the file extension associated with the index class."""
        return cls._EXT
