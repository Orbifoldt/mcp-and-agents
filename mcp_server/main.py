import contextlib

from fastmcp import FastMCP

from mcp_server.math_tools import math_mcp

mcp = FastMCP(on_duplicate="error")
mcp.mount(math_mcp, namespace="math")


@mcp.tool(version="1.0.0")
def greet_v1(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool(version="2.0.0")
def greet_v2(name: str) -> str:
    return f"Hello there, {name}!"


async def main() -> None:
    await mcp.run_async(
        transport="http",
        host="0.0.0.0",  # noqa: S104
        port=8001,
    )


if __name__ == "__main__":
    import asyncio

    with contextlib.suppress(KeyboardInterrupt):  # asyncio will shut down, so this exception can be ignored
        asyncio.run(main())
