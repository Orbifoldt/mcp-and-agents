# Project structure
This is both an (agentic) application and a MCP server.

## Running it
For local development, run this to run the FastAPI server:
```shell
make app
```

And this for the MCP server:
```shell
make mcp
```


# MCP Server
Explore tools via the FastMCP cli:
```shell
uv run fastmcp list http://localhost:8001/mcp --transport http --json
```


# App
To be created...