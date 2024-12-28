from abc import ABC, abstractmethod
from datetime import datetime, timezone
from globals import DB_SESSION, LOGGER
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
    def __init__(self, provider_instance_id : int) -> None:
        self._provider_instance_id = provider_instance_id
        self._status = True
        self._data = None
        self._index_path = None
        LOGGER.info(f"Created provider object for {self._provider_instance_id}.")

    @abstractmethod
    def run(self) -> bool:
        pass

    def kill(self):
        self._status = False

    @property
    def status(self):
        return self._status

    @property
    def provider_instance_id(self):
        return self._provider_instance_id

    @property
    def last_indexed(self) -> None | datetime:
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._provider_instance_id).first()
            if instance != None:
                return instance.last_indexed

    @property
    def data(self) -> None | dict:
        if self._data == None:
            with DB_SESSION() as session:
                instance = session.query(ProviderInstance).filter_by(id=self._provider_instance_id).first()
                if instance != None:
                    self._data = instance.data
        return self._data

    @property
    def index_path(self) -> None | str:
        if self._index_path == None:
            with DB_SESSION() as session:
                instance = session.query(ProviderInstance).filter_by(id=self._provider_instance_id).first()
                if instance != None:
                    self._index_path = f"{INDEX_PATH}/{instance.name}_{instance.id}"
        return self._index_path

    def update_last_indexed(self) -> None:
        with DB_SESSION() as session:
            instance = session.query(ProviderInstance).filter_by(id=self._provider_instance_id).first()
            if instance != None:
                instance.last_indexed = datetime.now(tz=timezone.utc)
                session.commit()
            else:
                LOGGER.error(f"No matching provider instance found with key {self._provider_instance_id}. Can't update timestamp.")

    @classmethod
    def provider_id(cls):
        return cls._ID

    @classmethod
    def register_provider(cls) -> None:
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls._ID)
            if provider == None:
                provider = Provider(id=cls._ID, name=cls._NAME, desc=cls._DESCRIPTION, avatar=cls._AVATAR, schema=cls._SCHEMA)
                session.add(provider)
                session.commit()
