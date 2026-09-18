from collections.abc import Callable
from functools import lru_cache

from azure.core.credentials import TokenCredential
from azure.identity import ClientSecretCredential, get_bearer_token_provider

from common.settings import get_settings


@lru_cache
def get_client_secret_credential() -> TokenCredential:

    settings = get_settings()
    return ClientSecretCredential(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_npa_client_id,
        client_secret=settings.azure_npa_client_secret.get_secret_value(),
    )


def create_bearer_token_provider() -> Callable[[], str]:
    return get_bearer_token_provider(
        get_client_secret_credential(),
        "https://cognitiveservices.azure.com/.default",
    )
