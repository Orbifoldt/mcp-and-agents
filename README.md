# Project structure
This explores various agent frameworks and how they integrate with an MCP server and produce telemetry to Phoenix.

## Running it
For local development, run this to run the FastAPI server:
```shell
make app
```

And this for the MCP server:
```shell
make mcp
```
And for phoenix, running at [http://localhost:6006](http://localhost:6006):
```shell
make phoenix-up
make phoenix-logs
```

Then, for example, run:
```shell
curl --silent http://127.0.0.1:8000/agent-langchain/mcp?q=What%27s%2012%20times%203%20plus%204? | jq
```



# MCP Server
Explore tools via the FastMCP cli:
```shell
uv run fastmcp list http://localhost:8001/mcp --transport http --json
```


# App
Has various endpoints for the different frameworks:

## Endpoints

- Langgraph:
  - `GET /agent-langgraph?q=<question>`
  - `GET /agent-langgraph/mcp?q=<question>`
- Langchain:
  - `GET /agent-langchain?q=<question>`
  - `GET /agent-langchain/mcp?q=<question>`
  - `GET /agent-langchain/deep?q=<question>`  (for a `deep_agent`, here forcing it to use a todo-list tool, just for demonstration purposes)
- OpenAI:
  - `GET /agent-openai?q=<question>`
  - `GET /agent-openai/mcp?q=<question>`
- Strands:
  - `GET /agent-strands?q=<question>`
  - `GET /agent-strands/full-history?q=<question>` (showing how you could potentially access the full LLM conversation, not just the final message)
  - `GET /agent-strands/mcp?q=<question>`
