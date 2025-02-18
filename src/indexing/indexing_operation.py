from enum import Enum
from provider.utils.pipeline import ProcessedDocument
from schema.document.sub_document import SubDocument

class IndexingOperationType(Enum):
    """
    Enum representing indexing operations.
    
    Index updates are handled as DELETE followed by INSERT.
    """
    INSERT = 1  # Add a new document
    DELETE = 2  # Remove an existing document

class IndexingOperation:
    """
    Represents an indexing operation (INSERT or DELETE) applied to a SubDocument.
    
    Attributes:
        _value (SubDocument): The document involved in the operation.
        _operation (IndexingOperationType): The type of indexing operation.
    """

    def __init__(self, value: ProcessedDocument, operation: IndexingOperationType):
        """
        Initializes an IndexingOperation.

        Args:
            value (SubDocument): The document associated with the operation.
            operation (IndexingOperationType): The operation type (INSERT or DELETE).

        Raises:
            ValueError: If the provided operation is not a valid IndexingOperationType.
        """
        self._value = value
        self._operation = operation

    @property
    def value(self) -> ProcessedDocument:
        """
        Returns the document associated with this operation.

        Returns:
            SubDocument: The sub-document instance.
        """
        return self._value

    @property
    def operation(self) -> IndexingOperationType:
        """
        Returns the type of indexing operation (INSERT or DELETE).

        Returns:
            IndexingOperationType: The operation type.
        """
        return self._operation

    def __repr__(self) -> str:
        """
        Returns a string representation of the IndexingOperation.
        
        Returns:
            str: A readable string representation.
        """
        return f"IndexingOperation(value={self._value}, operation={self._operation.name})"

    def __eq__(self, other) -> bool:
        """
        Checks equality between two IndexingOperation instances.

        Args:
            other (IndexingOperation): The other instance to compare.

        Returns:
            bool: True if both instances have the same value and operation type, otherwise False.
        """
        if not isinstance(other, IndexingOperation):
            return False
        return self._value == other._value and self._operation == other._operation

    def __hash__(self) -> int:
        """
        Returns a hash value, making this class suitable for use in sets and dictionaries.

        Returns:
            int: The hash of the object.
        """
        return hash((self._value, self._operation))
