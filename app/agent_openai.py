from functools import lru_cache
from typing import Any

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStreamableHttp
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from fastapi import APIRouter
from openai import AsyncAzureOpenAI

from app.azure.auth import create_bearer_token_provider
from common.settings import get_settings

INSTRUCTIONS = (
    "You are a helpful assistant tasked with performing arithmetic on a set of "
    "inputs. Answer in a nice English sentence, repeating the question in your "
    "own words and answering it."
)


@lru_cache
def get_model() -> OpenAIChatCompletionsModel:
    settings = get_settings()
    model_config = settings.gpt_5_6_luna

    client = AsyncAzureOpenAI(
        azure_endpoint=settings.llm_endpoint,
        azure_deployment=model_config.deployment_name,
        api_version=model_config.api_version,
        azure_ad_token_provider=create_bearer_token_provider(),
    )
    return OpenAIChatCompletionsModel(
        model=model_config.deployment_name,
        openai_client=client,
    )


@function_tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""

    return a * b


@function_tool
def add(a: int, b: int) -> int:
    """Add two integers."""

    return a + b


@function_tool
def divide(a: int, b: int) -> float:
    """Divide one integer by another."""

    return a / b


agent_router_openai = APIRouter(prefix="/agent-openai", tags=["agent"])


@agent_router_openai.get("")
async def try_agent(q: str) -> str:
    agent = Agent(
        name="Arithmetic assistant",
        instructions=INSTRUCTIONS,
        model=get_model(),
        tools=[add, multiply, divide],
        mcp_servers=[],
    )
    result = await Runner.run(agent, q)
    return result.final_output


@agent_router_openai.get("/mcp")
async def try_mcp_agent(q: str) -> str:
    async with MCPServerStreamableHttp(
        params={"url": "http://localhost:8001/mcp"},
        name="local math MCP server",
    ) as mcp_server:
        agent = Agent(
            name="Arithmetic assistant",
            instructions=INSTRUCTIONS,
            model=get_model(),
            tools=[],
            mcp_servers=[mcp_server],
        )
        result = await Runner.run(agent, q)
        return result.final_output
