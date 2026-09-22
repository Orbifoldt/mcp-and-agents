from typing import TYPE_CHECKING, Any

from fastapi import APIRouter
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import HumanMessage, SystemMessage, ToolCall
from langchain.tools import tool
from langchain_core.messages import AIMessage
from langchain_openai import AzureChatOpenAI
from langgraph.func import entrypoint, task
from langgraph.graph import add_messages
from langgraph.graph.message import Messages

from app.azure.auth import create_bearer_token_provider
from common.settings import get_settings

if TYPE_CHECKING:
    from langchain.agents.middleware import OutputAgentState

INSTRUCTIONS = (
    "You are a helpful assistant tasked with performing arithmetic on a set of "
    "inputs. Answer in a nice English sentence, repeating the question in your "
    "own words and answering it."
)


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


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


agent_router_lang_graph = APIRouter(prefix="/agent-langgraph", tags=["agent"])


model = get_chat_model()
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


@task
def call_llm(message: Messages) -> AIMessage:
    # pyrefly: ignore [bad-argument-type]
    return model_with_tools.invoke([SystemMessage(content=INSTRUCTIONS), *message])


@task
def call_tool(tool_call: ToolCall) -> Any:  # noqa: ANN401
    tool = tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call)


@entrypoint()
def agent(messages: Messages) -> Messages:
    model_response = call_llm(messages).result()

    while True:
        if not model_response.tool_calls:
            break

        tool_futures = [call_tool(tool_call) for tool_call in model_response.tool_calls]
        tool_results = [future.result() for future in tool_futures]
        messages = add_messages(messages, [model_response, *tool_results])
        model_response = call_llm(messages).result()

    return add_messages(messages, [model_response])


@agent_router_lang_graph.get("")
def try_agent(q: str) -> Any:  # noqa: ANN401
    stream = agent.stream_events([HumanMessage(content=q)], version="v3")

    out = list(stream)
    return out[-1]["params"]["data"][-1].content[0]["text"]  # Wow, such a nice dev experience


@agent_router_lang_graph.get("/mcp")
async def try_mcp_agent(q: str) -> Any:  # noqa: ANN401
    the_model = get_chat_model()
    async with MCPAdapter("http://localhost:8001/mcp") as adapter:
        mcp_tools = await adapter.list_tools()

        agent_with_mcp = create_agent(
            model=the_model,
            tools=mcp_tools,
        )

        initial_msg = SystemMessage(content=INSTRUCTIONS)
        # pyrefly: ignore [bad-assignment]
        result: OutputAgentState = await agent_with_mcp.ainvoke(
            {"messages": [initial_msg, HumanMessage(content=q)]},
        )
        return result
