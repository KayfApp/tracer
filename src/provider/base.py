from abc import ABC, abstractmethod
from datetime import datetime

from src.schema.connections.provider_instance import ProviderInstance


class BaseProvider(ABC):
    def __init__(self, data : ProviderInstance) -> None:
        self.__data = data

    @abstractmethod
    def run(self) -> bool:
        pass

    def update_last_indexed(self) -> None:
        pass
