from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


async def main():
    await mcp.run_async(
        transport="http",
        host="0.0.0.0",
        port=8001,
    )


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # asyncio will shut down, so this exception can be ignored
