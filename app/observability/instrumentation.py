from functools import lru_cache

from fastapi import FastAPI

from app.observability.phoenix import get_phoenix_tracer_provider


def instrument_app(application: FastAPI, tracer_provider: object) -> None:
    """Instrument standard application and HTTP activity."""

    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(
        application,
        tracer_provider=tracer_provider,
    )


def instrument_ai(tracer_provider: object) -> None:
    """Instrument LangChain/LangGraph and direct OpenAI activity."""

    from openinference.instrumentation.langchain import LangChainInstrumentor
    from openinference.instrumentation.openai import OpenAIInstrumentor

    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


@lru_cache
def configure_observability(application: FastAPI) -> None:
    """Configure all enabled observability for a FastAPI application."""

    tracer_provider = get_phoenix_tracer_provider()
    if tracer_provider is None:
        return

    instrument_app(application, tracer_provider)
    instrument_ai(tracer_provider)
