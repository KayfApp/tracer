from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from queue import Queue
from indexing.index_registry import IndexRegistry, IndexRegistryEvent, IndexRegistryObserver
from env import INDEXING_THREADS, FETCHING_TIME
from globals import LOGGER

class IndexingQueue(IndexRegistryObserver):
    _GLOBAL_INSTANCE = None

    def __init__(self, index_registry: IndexRegistry) -> None:
        self._index_registry = index_registry
        self._index_registry.attach(self)
        self._status = True

    @staticmethod
    def instance():
        if(IndexingQueue._GLOBAL_INSTANCE == None):
            IndexingQueue._GLOBAL_INSTANCE = IndexingQueue(IndexRegistry.instance())
        return IndexingQueue._GLOBAL_INSTANCE

    def notify(self, event: IndexRegistryEvent, target: int):
        if event == IndexRegistryEvent.ADD:
            pass
        elif event == IndexRegistryEvent.REMOVE:
            pass # NOTE: No need for a manual remove as instance kills itself
