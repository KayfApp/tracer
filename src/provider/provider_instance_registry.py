
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Type, List
from threading import Lock

from provider.generic_provider import GenericProvider
from globals import DB_SESSION
from schema.connections.provider import Provider

class ProviderInstanceRegistryEvent(Enum):
    """Enum for events that notify observers of changes in the ProviderInstanceRegistry."""
    ADD = 1
    REMOVE = 2

class ProviderInstanceRegistryObserver(ABC):
    """Abstract base class for observers that want to be notified of events in the ProviderInstanceRegistry."""
    @abstractmethod
    def notify(self, event: ProviderInstanceRegistryEvent, target: int) -> None:
        """Notifies the observer of a registry event.

        Args:
            event (ProviderInstanceRegistryEvent): The event that occurred.
            target (int): The ID of the provider instance affected.
        """
        pass

class ProviderInstanceRegistry:
    """Singleton registry for managing provider instances and notifying observers of changes."""
    _GLOBAL_INSTANCE: Optional["ProviderInstanceRegistry"] = None

    def __init__(self) -> None:
        self._registry: Dict[int, GenericProvider] = {}
        self._observers: List[ProviderInstanceRegistryObserver] = []
        self._lock = Lock()  # Lock for thread safety

    @staticmethod
    def instance() -> "ProviderInstanceRegistry":
        """Gets the singleton instance of the ProviderInstanceRegistry.

        Returns:
            ProviderInstanceRegistry: The singleton instance.
        """
        if ProviderInstanceRegistry._GLOBAL_INSTANCE is None:
            ProviderInstanceRegistry._GLOBAL_INSTANCE = ProviderInstanceRegistry()
        return ProviderInstanceRegistry._GLOBAL_INSTANCE

    def attach(self, observer: ProviderInstanceRegistryObserver) -> None:
        """Attaches an observer to be notified of changes in the registry.

        Args:
            observer (ProviderInstanceRegistryObserver): The observer to attach.
        """
        with self._lock:  # Ensure thread safety when modifying observers
            self._observers.append(observer)

    def detach(self, observer: ProviderInstanceRegistryObserver) -> None:
        """Detaches an observer from the registry.

        Args:
            observer (ProviderInstanceRegistryObserver): The observer to detach.
        """
        with self._lock:  # Ensure thread safety when modifying observers
            self._observers.remove(observer)

    def _notify_all(self, event: ProviderInstanceRegistryEvent, target: int) -> None:
        """Notifies all observers of a registry event.

        Args:
            event (ProviderInstanceRegistryEvent): The event that occurred.
            target (int): The ID of the provider instance affected.
        """
        for o in self._observers:
            o.notify(event, target)

    def add(self, key: int, value: GenericProvider) -> bool:
        """Adds a provider instance to the registry.

        Args:
            key (int): The ID of the provider instance.
            value (GenericProvider): The provider instance to add.

        Returns:
            bool: True if the instance was added, False if it already exists.
        """
        with self._lock:  # Ensure thread safety when modifying the registry
            if key in self._registry:
                return False
            self._registry[key] = value
        self._notify_all(ProviderInstanceRegistryEvent.ADD, key)
        return True

    def remove(self, key: int) -> None:
        """Removes a provider instance from the registry.

        Args:
            key (int): The ID of the provider instance to remove.
        """
        with self._lock:  # Ensure thread safety when modifying the registry
            if key not in self._registry:
                return

            self._registry[key].kill()
            self._registry.pop(key)
            self._notify_all(ProviderInstanceRegistryEvent.REMOVE, key)

    def get(self, key: int) -> Optional[GenericProvider]:
        """Retrieves a provider instance by its ID.

        Args:
            key (int): The ID of the provider instance.

        Returns:
            Optional[GenericProvider]: The provider instance, or None if not found.
        """
        with self._lock:  # Ensure thread safety when accessing the registry
            return self._registry.get(key, None)

    def load_instances(self, cls: Type[GenericProvider]) -> None:
        """Loads provider instances of a given class from the database and adds them to the registry.

        Args:
            cls (Type[GenericProvider]): The class of the provider to load instances for.
        """
        with DB_SESSION() as session:
            provider = session.query(Provider).filter_by(id=cls.provider_id()).first()
            if provider is not None:
                instances = provider.instances
                for instance in instances:
                    self.add(instance.id, cls(instance.id))
