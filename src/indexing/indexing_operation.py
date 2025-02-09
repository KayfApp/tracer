from enum import Enum

from schema.document.sub_document import SubDocument

class IndexingOperationType(Enum):
    INSERT = 1
    UPDATE = 2
    DELETE = 3

class IndexingOperation:
    def __init__(self, value : SubDocument, operation: IndexingOperationType):
        self._value = value
        self._operation = operation

    @property
    def value(self):
        return self._value

    @property
    def operation(self):
        return self._operation

