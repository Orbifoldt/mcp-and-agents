from functools import lru_cache

from azure.identity import ClientSecretCredential, get_bearer_token_provider
from openai import AzureOpenAI

from common.settings import get_settings


@lru_cache
def get_openai_client() -> AzureOpenAI:
    """Return the shared Azure OpenAI client."""

    settings = get_settings()
    credential = ClientSecretCredential(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_npa_client_id,
        client_secret=settings.azure_npa_client_secret.get_secret_value(),
    )
    token_provider = get_bearer_token_provider(
        credential,
        "https://cognitiveservices.azure.com/.default",
    )

    return AzureOpenAI(
        azure_endpoint=settings.llm_endpoint,
        api_version=settings.gpt_5_6_luna.api_version,
        azure_ad_token_provider=token_provider,
    )
