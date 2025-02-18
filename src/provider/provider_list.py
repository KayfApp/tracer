from typing import Dict, Type

from provider.email.imap import ImapProvider
from provider.generic_provider import GenericProvider
from provider.provider_instance_registry import ProviderInstanceRegistry

# List of provider classes to load
PROVIDERS: list[Type[GenericProvider]] = [ImapProvider]

def load_providers() -> None:
    """Loads all registered providers and initializes their instances in the ProviderInstanceRegistry.

    This function iterates over the PROVIDERS list, registers each provider, and loads its instances
    into the ProviderInstanceRegistry.
    """
    for p in PROVIDERS:
        p.register_provider()
        ProviderInstanceRegistry.instance().load_instances(p)

internal_mapping: Dict[str, Type[GenericProvider]] = {}

def mapping() -> Dict[str, Type[GenericProvider]]:
    """Creates and returns a mapping of provider IDs to their corresponding provider classes.

    If the mapping has not been created yet, it initializes it by iterating through the PROVIDERS list.

    Returns:
        Dict[str, Type[GenericProvider]]: A dictionary mapping provider IDs to provider classes.
    """
    if len(internal_mapping) == 0:
        for p in PROVIDERS:
            internal_mapping[p.provider_id()] = p
    return internal_mapping
