from abc import ABC, abstractmethod
from datetime import datetime, timezone
from queue import Queue, Empty
from globals import DB_SESSION, LOGGER
from indexing.indexing_operation import IndexingOperation
from schema.connections.provider_instance import ProviderInstance
from env import INDEX_PATH
from schema.connections.provider import Provider

class GenericProvider(ABC):
    _ID="GENERIC@KAYF:1.0"
    _NAME="GENERIC"
    _DESCRIPTION="GENERIC PROVIDER"
    _AVATAR=""
    _SCHEMA={}

    """
    Provider implementation without API specifics. Offers functions to manage and populate indices.
    Actual provider implementations only need to inherit from this class and override the run() function.
    """
    def __init__(self, id : int) -> None:
        self._id = id
        self._status = True
        self._indexing_queue: Queue[IndexingOperation] = Queue()

        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance != None:
                self._data = instance.data
                self._index_path = f"{INDEX_PATH}/{self._NAME}/{instance.name}_{instance.id}"
            else:
                session.close()
                raise LookupError(f"{id} not found")
        LOGGER.info(f"Created provider object for {self._id}.")

    @abstractmethod
    def run(self) -> bool:
        pass

    def kill(self):
        self._status = False

    @property
    def status(self):
        return self._status

    @property
    def id(self):
        return self._id

    @property
    def last_indexed(self) -> None | datetime:
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance != None:
                return instance.last_indexed.replace(tzinfo=timezone.utc)

    @property
    def data(self) -> dict:
        return self._data

    @property
    def index_path(self) -> str:
        return self._index_path

    def update_last_indexed(self, time: datetime | None) -> None:
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._id).first()
            if instance != None:
                if time == None:
                    instance.last_indexed = datetime.now(tz=timezone.utc)
                else:
                    instance.last_indexed = time
                session.commit()
            else:
                LOGGER.error(f"No matching provider instance found with key {self._id}. Can't update timestamp.")

    def push(self, value):
        self._indexing_queue.put(value)

    def pop(self):
        return self._indexing_queue.get()

    def pop_nowait(self):
        try:
            return self._indexing_queue.get()
        except Empty:
            return None

    @classmethod
    def provider_id(cls):
        return cls._ID

    @classmethod
    def register_provider(cls) -> None:
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls._ID).first()
            if provider == None:
                provider = Provider(id=cls._ID, name=cls._NAME, desc=cls._DESCRIPTION, avatar=cls._AVATAR, schema=cls._SCHEMA)
                session.add(provider)
                session.commit()
