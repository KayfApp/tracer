from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from provider.generic_provider import GenericProvider
from env import INDEXING_THREADS, INDEXING_TIME
from globals import LOGGER

class ProviderQueue:
    _GLOBAL_INSTANCE = None

    def __init__(self) -> None:
        self._indexing_queue : Queue[GenericProvider] = Queue()
        self._status = True
        self._thread = Thread(target = self.run)

    @staticmethod
    def instance():
        if(ProviderQueue._GLOBAL_INSTANCE == None):
            ProviderQueue._GLOBAL_INSTANCE = ProviderQueue()
        return ProviderQueue._GLOBAL_INSTANCE

    def push(self, val : GenericProvider) -> None:
        self._indexing_queue.put(val)

    def _pop(self) -> GenericProvider:
        return self._indexing_queue.get()

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._status = False
        self._indexing_queue.shutdown(immediate=True)

    def _execute_unit(self, provider_instance : GenericProvider):
        index_sucessful = provider_instance.run()
        if index_sucessful:
            LOGGER.info(f'Sucessfully indexed {provider_instance.id}.')
        else:
            LOGGER.error(f'Indexing {provider_instance.id} failed.')
        if provider_instance.status:
            self.push(provider_instance)
        else:
            LOGGER.info(f"Removing {provider_instance.id} from the indexing queue.")

    def run(self) -> None:
       with ThreadPoolExecutor(max_workers=INDEXING_THREADS) as executor:
           while self._status:
               provider_instance = self._pop()
               last_indexed = provider_instance.last_indexed
               if(last_indexed != None and provider_instance.status):
                   deltatime = last_indexed - datetime.now(tz=timezone.utc)
                   if abs(deltatime.total_seconds()) >= INDEXING_TIME:
                        executor.submit(
                                lambda: self._execute_unit(provider_instance)
                        )
                   else:
                        if provider_instance.status:
                            self.push(provider_instance)
                        else:
                            LOGGER.info(f"Removing {provider_instance.id} from the indexing queue.")
