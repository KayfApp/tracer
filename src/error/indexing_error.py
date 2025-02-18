from globals import LOGGER

class IndexingError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        LOGGER.error(f"IndexingError: {message}")

    def __str__(self):
        return f"IndexingError: {self.message}"
