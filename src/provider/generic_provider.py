from typing import Optional
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import os
from queue import Queue, Empty
from globals import DB_SESSION, LOGGER
from indexing.indexing_operation import IndexingOperation
from schema.connections.provider_instance import ProviderInstance
from env import INDEX_PATH
from schema.connections.provider import Provider

class GenericProvider(ABC):
    """Abstract base class for provider implementations without API specifics.
    
    This class offers functions to manage and populate indices. 
    Actual provider implementations need to inherit from this class and 
    override the `run()` method.
    """
    _ID = "GENERIC@KAYF:1.0"
    _NAME = "GENERIC"
    _DESCRIPTION = "GENERIC PROVIDER"
    _AVATAR = ""
    _SCHEMA = {}

    def __init__(self, id: int) -> None:
        """Initializes a GenericProvider instance.

        Args:
            id (int): The ID of the provider instance.

        Raises:
            LookupError: If the provider instance with the given ID is not found.
        """
        self._id = id
        self._status = True
        self._indexing_queue: Queue[IndexingOperation] = Queue()
        self._last_indexed = datetime.min.replace(tzinfo=timezone.utc)
        self._setup_completed = False

        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance is not None:
                self._data = instance.data
                self._index_path = f"{INDEX_PATH}/{self._NAME}/{instance.name}_{instance.id}"
                if not os.path.exists(self._index_path):
                    try:
                        os.makedirs(self._index_path)
                    except PermissionError:
                        LOGGER.error(f"Can't create directory due to lack of permissions! {self._index_path}")
            else:
                session.close()
                raise LookupError(f"Provider instance with ID {id} not found.")
        
        LOGGER.info(f"Created provider object for {self._id}.")

    @abstractmethod
    def _setup(self) -> bool:
        """Sets up the provider.

        Returns:
            bool: True if setup is successful, False otherwise.
        """
        pass

    @abstractmethod
    def run(self) -> bool:
        """Runs the provider's main logic.

        Returns:
            bool: True if the run was successful, False otherwise.
        """
        if not self._setup_completed:
            self._setup_completed = True
            return self._setup()
        return True

    @abstractmethod
    def _clean_up(self) -> None:
        """Cleans up resources when the provider is killed."""
        pass

    def kill(self) -> None:
        """Terminates the provider's operation and cleans up resources."""
        self._status = False
        self._clean_up()
        if os.path.exists(self._index_path):
            try:
                os.rmdir(self._index_path)
            except PermissionError:
                LOGGER.error(f"Can't delete directory due to lack of permissions! {self._index_path}")


    @property
    def status(self) -> bool:
        """Gets the current status of the provider.

        Returns:
            bool: True if the provider is active, False otherwise.
        """
        return self._status

    @property
    def id(self) -> int:
        """Gets the ID of the provider instance.

        Returns:
            int: The ID of the provider instance.
        """
        return self._id

    @property
    def last_fetched(self) -> Optional[datetime]:
        """Gets the last fetched timestamp from the database.

        Returns:
            Optional[datetime]: The last fetched timestamp, or None if not found.
        """
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance is not None:
                return instance.last_fetched.replace(tzinfo=timezone.utc)
            return None

    @property
    def last_indexed(self) -> datetime:
        """Gets the last indexed timestamp.

        Returns:
            datetime: The last indexed timestamp.
        """
        return self._last_indexed

    @property
    def data(self) -> dict:
        """Gets the data associated with the provider instance.

        Returns:
            dict: The provider instance data.
        """
        return self._data

    @property
    def index_path(self) -> str:
        """Gets the path where the index is stored.

        Returns:
            str: The index path.
        """
        return self._index_path

    def update_last_fetched(self, time: Optional[datetime]) -> None:
        """Updates the last fetched timestamp in the database.

        Args:
            time (Optional[datetime]): The new last fetched time, or None to set to now.
        """
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance is not None:
                instance.last_fetched = time or datetime.now(tz=timezone.utc)
                session.commit()
            else:
                LOGGER.error(f"No matching provider instance found with key {self._id}. Can't update timestamp.")

    def update_last_indexed(self) -> None:
        """Updates the last indexed timestamp to the current time."""
        self._last_indexed = datetime.now(tz=timezone.utc)

    @property
    def queue_empty(self) -> bool:
        """Checks if the indexing queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return self._indexing_queue.qsize() == 0

    def push(self, value: IndexingOperation) -> None:
        """Pushes a new indexing operation onto the queue.

        Args:
            value (IndexingOperation): The indexing operation to add to the queue.
        """
        self._indexing_queue.put(value)

    def pop(self) -> IndexingOperation:
        """Removes and returns the next indexing operation from the queue.

        Returns:
            IndexingOperation: The next indexing operation in the queue.
        """
        return self._indexing_queue.get()

    def pop_nowait(self) -> Optional[IndexingOperation]:
        """Removes and returns the next indexing operation from the queue without blocking.

        Returns:
            Optional[IndexingOperation]: The next indexing operation, or None if the queue is empty.
        """
        try:
            return self._indexing_queue.get_nowait()
        except Empty:
            return None

    @classmethod
    def provider_id(cls) -> str:
        """Gets the unique provider ID for this provider class.

        Returns:
            str: The provider ID.
        """
        return cls._ID

    @classmethod
    def register_provider(cls) -> None:
        """Registers the provider in the database."""
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls._ID).first()
            if provider is None:
                provider = Provider(id=cls._ID, name=cls._NAME, desc=cls._DESCRIPTION, avatar=cls._AVATAR, schema=cls._SCHEMA)
                session.add(provider)
                session.commit()
