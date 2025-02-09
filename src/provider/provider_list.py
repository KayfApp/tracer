from typing import Dict, Type

from provider.email.imap import ImapProvider
from provider.generic_provider import GenericProvider
from provider.provider_instance_registry import ProviderInstanceRegistry

PROVIDERS: list[Type[GenericProvider]] = [ImapProvider]

def load_providers():
    for p in PROVIDERS:
        p.register_provider()
        ProviderInstanceRegistry.instance().load_instances(p)

internal_mapping = {}

def mapping() -> Dict[str, Type[GenericProvider]]:
    if len(internal_mapping) == 0:
        for p in PROVIDERS:
            internal_mapping[p.provider_id()] = p
    return internal_mapping
