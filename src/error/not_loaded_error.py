from globals import LOGGER

class NotLoadedError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        LOGGER.error(f"NotLoadedError: {message}")

    def __str__(self):
        return f"NotLoadedError: {self.message}"
