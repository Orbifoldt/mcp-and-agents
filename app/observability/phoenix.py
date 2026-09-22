from functools import lru_cache

from openinference.instrumentation.strands_agents import StrandsAgentsToOpenInferenceProcessor
from opentelemetry.sdk.trace import SynchronousMultiSpanProcessor, SpanProcessor
from opentelemetry.trace import TracerProvider
from phoenix.otel import register

from common.settings import get_settings


@lru_cache
def get_phoenix_tracer_provider(initial_span_processor: SpanProcessor) -> TracerProvider | None:
    """Create and cache the Phoenix OpenTelemetry tracer provider."""
    settings = get_settings()
    if not settings.phoenix_enabled:
        return None

    active_span_processor = SynchronousMultiSpanProcessor()
    # Certain processors must be run before any other (phoenix) processors to ensure the mapping of span attributes
    active_span_processor.add_span_processor(initial_span_processor)

    endpoint = f"{settings.phoenix_collector_endpoint.rstrip('/')}/v1/traces"
    return register(
        project_name=settings.phoenix_project_name,
        endpoint=endpoint,
        batch=True,
        auto_instrument=False,
        verbose=False,
        active_span_processor=active_span_processor,
    )
