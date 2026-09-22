from functools import lru_cache
from typing import Any

from fastapi import APIRouter
from mcp.client.streamable_http import streamable_http_client
from strands import Agent, tool
from strands.agent import AgentResult
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient

from app.azure.openai_client import get_async_openai_client
from common.settings import get_settings

agent_router_strands = APIRouter(prefix="/agent-strands", tags=["agent"])

INSTRUCTIONS = (
    "You are a helpful assistant tasked with performing arithmetic on a set of "
    "inputs. Answer in a nice English sentence, repeating the question in your "
    "own words and answering it."
)


@lru_cache
def get_model() -> OpenAIModel:
    llm_model = get_async_openai_client()
    settings = get_settings()
    return OpenAIModel(
        client=llm_model,
        model_id=settings.gpt_5_6_luna.deployment_name,
        stream=False,
    )


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide one integer by another."""
    return a / b


@agent_router_strands.get("")
async def try_agent(q: str) -> Any:
    agent = Agent(
        model=get_model(),
        tools=[multiply, add, divide],
        system_prompt=INSTRUCTIONS,
    )
    result: AgentResult = agent(q)
    return result.message


@agent_router_strands.get("/full-history")
async def try_agent_full_history(q: str) -> Any:
    # A normal agent just gives the final result, like this we can get intermediary results (sort of...)
    agent = Agent(
        model=get_model(),
        tools=[multiply, add, divide],
        system_prompt=INSTRUCTIONS,
    )
    results = []
    async for ev in agent.stream_async(q):
        if ev.get("type") == "tool_use_stream":
            results.append(ev.get("current_tool_use"))
        if ev.get("messages") is not None:
            # This event can get sent twice, so not really nice like so
            results.append(ev.get("messages"))
    return results


@agent_router_strands.get("/mcp")
async def try_agent_with_mcp(q: str) -> Any:
    mcp = MCPClient(lambda: streamable_http_client(url= "http://localhost:8001/mcp"))
    with mcp:
        tools = mcp.list_tools_sync()
        agent = Agent(
            model=get_model(),
            tools=tools,
            system_prompt=INSTRUCTIONS,
        )
        result: AgentResult = agent(q)
        return result.message


