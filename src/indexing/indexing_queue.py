from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from provider.generic_provider import GenericProvider
from env import INDEXING_THREADS, INDEXING_TIME
from globals import LOGGER

class IndexingQueue:
    _GLOBAL_INSTANCE = None

    def __init__(self) -> None:
        self._indexing_queue : Queue[GenericProvider] = Queue()
        self._status = True
        self._thread = Thread(target = self.run)

    @staticmethod
    def instance():
        if(IndexingQueue._GLOBAL_INSTANCE == None):
            IndexingQueue._GLOBAL_INSTANCE = IndexingQueue()
        return IndexingQueue._GLOBAL_INSTANCE

    def push(self, val : GenericProvider) -> None:
        self._indexing_queue.put(val)

    def _pop(self) -> GenericProvider:
        return self._indexing_queue.get()

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._status = False
        self._indexing_queue.shutdown(immediate=True)

    def _execute_unit(self, to_index : GenericProvider):
        index_sucessful = to_index.run()
        if index_sucessful:
            LOGGER.info(f'Sucessfully indexed {to_index.provider_instance_id}.')
            to_index.update_last_indexed()
        else:
            LOGGER.error(f'Indexing {to_index.provider_instance_id} failed.')
        if to_index.status:
            self.push(to_index)
        else:
            LOGGER.info(f"Removing {to_index.provider_instance_id} from the indexing queue.")

    def run(self) -> None:
       with ThreadPoolExecutor(max_workers=INDEXING_THREADS) as executor:
           while self._status:
               to_index = self._pop()
               last_indexed = to_index.last_indexed
               if(last_indexed != None and to_index.status):
                   deltatime = last_indexed - datetime.now(tz=timezone.utc)
                   if deltatime.seconds >= INDEXING_TIME:
                        executor.submit(
                                lambda: self._execute_unit(to_index)
                        )
