from fastapi import FastAPI

from app.agent_lang_graph import agent_router_lang_graph
from app.agent_langchain import agent_router_langchain
from app.agent_openai import agent_router_openai
from app.azure.openai_client import simple_chat
from app.observability import configure_observability
from common.settings import get_settings

app = FastAPI()
configure_observability(app)

app.include_router(agent_router_lang_graph)
app.include_router(agent_router_langchain)
app.include_router(agent_router_openai)


@app.get("/")
async def read_root() -> dict:
    settings = get_settings()
    return {
        "Hello": "World",
        "Settings": settings.dict(),
        "msg": simple_chat(
            system_message="Assistent is HAL 9000, the computer aboard the space ship Discovery One. "
            "The user is called Dave.",
            user_message="Can you open the pod bay doors, HAL?",
        ),
    }
