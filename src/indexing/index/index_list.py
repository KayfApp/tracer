from typing import Dict, List, Type
from threading import Lock
from indexing.index.generic_index import GenericIndex
from indexing.index.store.faiss_index import FaissIndex

# List of available index types
INDICES: List[Type[GenericIndex]] = [FaissIndex]

# Internal mappings for file extensions to index classes
_internal_mapping: Dict[str, Type[GenericIndex]] = {}
_internal_file_extensions: List[str] = []

# Lock for thread safety
_mapping_lock = Lock()
_extensions_lock = Lock()

def mapping() -> Dict[str, Type[GenericIndex]]:
    """
    Returns a dictionary mapping file extensions to their corresponding index classes.

    Uses lazy initialization with thread safety to populate the mapping.

    Returns:
        Dict[str, Type[GenericIndex]]: A dictionary where keys are file extensions
        and values are index classes.
    """
    with _mapping_lock:
        if not _internal_mapping:
            for index_class in INDICES:
                _internal_mapping[index_class.extension().lower()] = index_class
    return _internal_mapping

def file_extensions() -> List[str]:
    """
    Returns a list of supported file extensions for indexing.

    Uses lazy initialization with thread safety to populate the list.

    Returns:
        List[str]: A list of file extensions supported by the indexing system.
    """
    with _extensions_lock:
        if not _internal_file_extensions:
            indices_mapping = mapping()
            for index_class in indices_mapping.values():
                _internal_file_extensions.append(index_class.extension().lower())
    return _internal_file_extensions

