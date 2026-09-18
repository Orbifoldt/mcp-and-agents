from collections.abc import Sequence
from functools import lru_cache
from typing import Any

from fastapi import APIRouter
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import HumanMessage
from langchain.tools import BaseTool, tool
from langchain_openai import AzureChatOpenAI

from app.azure.auth import create_bearer_token_provider
from common.settings import get_settings

INSTRUCTIONS = (
    "You are a helpful assistant tasked with performing arithmetic on a set of "
    "inputs. Answer in a nice English sentence, repeating the question in your "
    "own words and answering it."
)


@lru_cache
def get_chat_model() -> AzureChatOpenAI:
    settings = get_settings()
    model_config = settings.gpt_5_6_luna

    return AzureChatOpenAI(
        azure_endpoint=settings.llm_endpoint,
        azure_deployment=model_config.deployment_name,
        api_version=model_config.api_version,
        model=model_config.name,
        azure_ad_token_provider=create_bearer_token_provider(),
    )


@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add `a` and `b`."""
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`."""
    return a / b


LOCAL_TOOLS: list[BaseTool] = [add, multiply, divide]


async def _run_agent(question: str, tools: Sequence[BaseTool]) -> dict[str, Any]:
    agent = create_agent(
        model=get_chat_model(),
        tools=tools,
        system_prompt=INSTRUCTIONS,
        name="arithmetic-assistant",
    )
    return await agent.ainvoke({"messages": [HumanMessage(content=question)]})


agent_router_langchain = APIRouter(prefix="/agent-langchain", tags=["agent"])


@agent_router_langchain.get("")
async def try_agent(q: str) -> dict:
    return await _run_agent(q, LOCAL_TOOLS)


@agent_router_langchain.get("/mcp")
async def try_mcp_agent(q: str) -> dict:
    async with MCPAdapter("http://localhost:8001/mcp") as adapter:
        mcp_tools = await adapter.list_tools()
        return await _run_agent(q, mcp_tools)
