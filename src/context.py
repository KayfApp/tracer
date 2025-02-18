import threading
import secrets

class Context:
    def __init__(self, context_id: int, manager: 'ContextManager'):
        """
        Initialize a Context with a unique identifier and its parent ContextManager.
        """
        self._id = context_id
        self._manager = manager
        self._released = False

    def free(self):
        """
        Release this context, allowing its id to be reused.
        This should be called by any consumer (e.g., your index load/release methods)
        when the context is no longer needed.
        """
        if not self._released:
            self._released = True
            self._manager.free(self)

    @property
    def id(self):
        """The id property."""
        return self._id

    def __hash__(self):
        # Use the unique identifier as the basis for the hash.
        return hash(self.id)

    def __eq__(self, other):
        # Two Context instances are considered equal if their ids are equal.
        if isinstance(other, Context):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Context({self._id})"

class ContextManager:
    _GLOBAL_INSTANCE = None

    def __init__(self):
        """
        Initialize the ContextManager.
        It keeps track of all active (in-use) context IDs to ensure uniqueness.
        """
        self._active_context_ids = set()  # Set of IDs that are currently allocated.
        self._lock = threading.Lock()     # Protects the active context set.

    @staticmethod
    def instance():
        if(ContextManager._GLOBAL_INSTANCE == None):
            ContextManager._GLOBAL_INSTANCE  = ContextManager()
        return ContextManager._GLOBAL_INSTANCE

    def generate(self) -> Context:
        """
        Generate and return a new unique Context instance.
        The generated context's id is guaranteed to be unique among active contexts.
        """
        with self._lock:
            while True:
                new_id = secrets.randbits(64)
                if new_id not in self._active_context_ids:
                    self._active_context_ids.add(new_id)
                    return Context(new_id, self)

    def free(self, context: Context):
        """
        Mark the context as free, allowing its id to be reused.
        This method is called by the Context instance when its free() method is invoked.
        """
        with self._lock:
            self._active_context_ids.discard(context._id)
