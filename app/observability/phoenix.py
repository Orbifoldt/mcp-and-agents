from functools import lru_cache

from common.settings import get_settings


@lru_cache
def get_phoenix_tracer_provider() -> object | None:
    """Create and cache the Phoenix OpenTelemetry tracer provider."""

    settings = get_settings()
    if not settings.phoenix_enabled:
        return None

    from phoenix.otel import register

    endpoint = f"{settings.phoenix_collector_endpoint.rstrip('/')}/v1/traces"
    return register(
        project_name=settings.phoenix_project_name,
        endpoint=endpoint,
        batch=True,
        auto_instrument=False,
        verbose=False,
    )
