from functools import lru_cache

from openai import AzureOpenAI

from app.azure.auth import create_bearer_token_provider
from common.settings import get_settings


@lru_cache
def get_openai_client() -> AzureOpenAI:
    """Return the shared Azure OpenAI client."""
    settings = get_settings()
    return AzureOpenAI(
        azure_endpoint=settings.llm_endpoint,
        api_version=settings.gpt_5_6_luna.api_version,
        azure_ad_token_provider=create_bearer_token_provider(),
    )


def simple_chat(system_message: str, user_message: str) -> str | None:
    llm = get_openai_client()
    settings = get_settings()
    result = llm.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        model=settings.gpt_5_6_luna.deployment_name,
    )
    return result.choices[0].message.content
