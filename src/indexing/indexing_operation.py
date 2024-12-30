from enum import Enum

from schema.document.sub_document import SubDocument

class IndexingOperationType(Enum):
    INSERT = 1
    UPDATE = 2
    DELETE = 3

class IndexingOperation:
    def __init__(self, id: int, value : SubDocument, operation: IndexingOperationType):
        self._id = id
        self._value = value
        self._operation = operation

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @property
    def operation(self):
        return self._operation

