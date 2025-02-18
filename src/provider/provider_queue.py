from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Thread, Condition
from typing import Tuple
from sortedcontainers import SortedList
from env import FETCHING_THREADS, FETCHING_TIME
from globals import LOGGER
from provider.provider_instance_registry import ProviderInstanceRegistry, ProviderInstanceRegistryEvent, ProviderInstanceRegistryObserver

class ProviderQueue(ProviderInstanceRegistryObserver):
    """ 
    The ProviderQueue manages all provider instances and is responsible for executing the run-functions.
    The class manages a list of the instances sorted after their last execution date and attempts to reduce CPU time by introducing smart waiting mechanisms.
    """
    
    _GLOBAL_INSTANCE = None

    def __init__(self, instance_registry: ProviderInstanceRegistry) -> None:
        """Initializes the ProviderQueue with the provided instance registry.

        Args:
            instance_registry (ProviderInstanceRegistry): The registry of provider instances.
        """
        self._provider_instances = SortedList()
        self._instance_registry = instance_registry
        self._instance_registry.attach(self)
        self._status = True
        self._thread = Thread(target=self.run, daemon=True)
        
        self._condition = Condition()
        self._active_tasks = 0  # Track running tasks

    @staticmethod
    def instance() -> 'ProviderQueue':
        """ 
        Returns the singleton instance of ProviderQueue. Creates it if it does not exist.

        Returns:
            ProviderQueue: The singleton instance of the ProviderQueue.
        """
        if ProviderQueue._GLOBAL_INSTANCE is None:
            ProviderQueue._GLOBAL_INSTANCE = ProviderQueue(ProviderInstanceRegistry.instance())
        return ProviderQueue._GLOBAL_INSTANCE

    def notify(self, event: ProviderInstanceRegistryEvent, target: int) -> None:
        """Handles provider addition and removal, keeping the list sorted.

        Args:
            event (ProviderInstanceRegistryEvent): The event indicating a change in the provider instance.
            target (int): The ID of the provider instance affected by the event.
        """
        with self._condition:
            if event == ProviderInstanceRegistryEvent.ADD:
                provider_instance = self._instance_registry.get(target)
                if provider_instance:
                    last_fetched = provider_instance.last_fetched or datetime.min
                    self._provider_instances.add((last_fetched, target))
                    self._condition.notify()
            elif event == ProviderInstanceRegistryEvent.REMOVE:
                self._provider_instances = SortedList(
                    [p for p in self._provider_instances if p[1] != target]
                )

    def start(self) -> None:
        """Starts the provider queue processing thread."""
        self._thread.start()

    def stop(self) -> None:
        """Stops the provider queue processing thread."""
        self._status = False
        with self._condition:
            self._condition.notify_all()

    def run(self) -> None:
        """Main loop for processing provider instances."""
        with ThreadPoolExecutor(max_workers=FETCHING_THREADS) as executor:
            while self._status:
                with self._condition:
                    while not self._provider_instances and self._status:
                        LOGGER.info("No providers pending. Sleeping...")
                        self._condition.wait()

                while self._provider_instances:
                    if self._active_tasks >= FETCHING_THREADS:
                        LOGGER.info("Thread pool full, waiting for a free slot...")
                        with self._condition:
                            self._condition.wait()
                        break

                    first_entry = self._safe_peek()
                    if first_entry is None:
                        break

                    last_fetched, provider_instance_id = first_entry
                    provider_instance = self._instance_registry.get(provider_instance_id)

                    if not provider_instance:
                        LOGGER.error(f'Provider instance {provider_instance_id} does not exist in registry!')
                        with self._condition:
                            self._provider_instances.pop(0)
                        continue

                    now = datetime.now(tz=timezone.utc)
                    deltatime = now - last_fetched
                    time_remaining = FETCHING_TIME - deltatime.total_seconds()

                    if time_remaining > 0:
                        LOGGER.info(f"Provider {provider_instance.id} not ready. Sleeping for {time_remaining:.2f}s")
                        with self._condition:
                            self._condition.wait(timeout=time_remaining)
                    else:  # Check again due to changes that may occur during the timeout (for example DELETE events)
                        with self._condition:
                            self._provider_instances.pop(0)
                        self._submit_task(executor, provider_instance)

    def _submit_task(self, executor, provider_instance) -> None:
        """Submits a task to fetch data from the provider instance and updates active task count with proper synchronization.

        Args:
            executor: The ThreadPoolExecutor used to submit tasks.
            provider_instance: The provider instance to run.
        """
        with self._condition:
            self._active_tasks += 1

        def task_wrapper() -> None:
            """Executes provider fetching and manages task tracking."""
            try:
                success = provider_instance.run()
                if success:
                    LOGGER.info(f'Successfully indexed {provider_instance.id}.')
                else:
                    LOGGER.error(f'Fetching {provider_instance.id} failed.')
            finally:
                with self._condition:
                    self._active_tasks -= 1
                    self._condition.notify()

                # Re-insert provider with updated last_fetched
                with self._condition:
                    last_fetched = provider_instance.last_fetched or datetime.min
                    self._provider_instances.add((last_fetched, provider_instance.id))
                    self._condition.notify()

        executor.submit(task_wrapper)

    def _safe_peek(self) -> Tuple[datetime, int] | None:
        """Safely gets the first element from the sorted list, handling potential type issues.

        Returns:
            Tuple[datetime, int] | None: The first element as a tuple of last fetched time and provider instance ID, or None if empty.
        """
        with self._condition:
            if self._provider_instances:
                return self._provider_instances[0]  # pyright: ignore
            return None

