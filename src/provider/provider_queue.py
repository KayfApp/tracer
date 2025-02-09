from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from provider.generic_provider import GenericProvider
from env import INDEXING_THREADS, FETCHING_TIME
from globals import LOGGER
from provider.provider_instance_registry import ProviderInstanceRegistry, ProviderInstanceRegistryEvent, ProviderInstanceRegistryObserver

class ProviderQueue(ProviderInstanceRegistryObserver):
    _GLOBAL_INSTANCE = None

    def __init__(self, instance_registry: ProviderInstanceRegistry) -> None:
        self._indexing_queue : Queue[int] = Queue()
        self._instance_registry = instance_registry
        self._instance_registry.attach(self)
        self._status = True
        self._thread = Thread(target = self.run)

    @staticmethod
    def instance():
        if(ProviderQueue._GLOBAL_INSTANCE == None):
            ProviderQueue._GLOBAL_INSTANCE = ProviderQueue(ProviderInstanceRegistry.instance())
        return ProviderQueue._GLOBAL_INSTANCE

    def notify(self, event: ProviderInstanceRegistryEvent, target: int):
        if event == ProviderInstanceRegistryEvent.ADD:
            self._push(target)
        elif event == ProviderInstanceRegistryEvent.REMOVE:
            pass # NOTE: No need for a manual remove as instance kills itself

    def _push(self, val : int) -> None:
        self._indexing_queue.put(val)

    def _pop(self) -> int:
        return self._indexing_queue.get()

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._status = False
        self._indexing_queue.shutdown(immediate=True)

    def _execute_unit(self, provider_instance: GenericProvider):
        index_sucessful = provider_instance.run()
        if index_sucessful:
            LOGGER.info(f'Sucessfully indexed {provider_instance.id}.')
        else:
            LOGGER.error(f'Indexing {provider_instance.id} failed.')
        if provider_instance.status:
            self._push(provider_instance.id)
        else:
            LOGGER.info(f"Removing {provider_instance.id} from the indexing queue.")

    def run(self) -> None:
       with ThreadPoolExecutor(max_workers=INDEXING_THREADS) as executor:
           while self._status:
               provider_instance_id = self._pop()
               provider_instance = self._instance_registry.get(provider_instance_id)
               if provider_instance == None:
                    LOGGER.error(f'Provider instance {provider_instance_id} does not exist in registry!')
                    continue

               last_indexed = provider_instance.last_fetched
               if(last_indexed != None and provider_instance.status):
                   deltatime = datetime.now(tz=timezone.utc) - last_indexed
                   if abs(deltatime.total_seconds()) >= FETCHING_TIME:
                        executor.submit(
                            self._execute_unit, provider_instance
                        )
                   else:
                        if provider_instance.status:
                            self._push(provider_instance_id)
                        else:
                            LOGGER.info(f"Removing {provider_instance_id} from the indexing queue.")
