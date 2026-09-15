from fastapi import FastAPI

from app.observability import configure_observability

app = FastAPI()
configure_observability(app)

from app.agent_lang_graph import agent_router_lang_graph
from app.azure.openai_client import simple_chat
from common.settings import get_settings

app.include_router(agent_router_lang_graph)

@app.get("/")
async def read_root():
    settings = get_settings()
    return {"Hello": "World", "Settings": settings.dict(),
            "msg": simple_chat(
                system_message="Assistent is HAL 9000, the computer aboard the space ship Discovery One. "
                               "The user is called Dave.",
                user_message="Can you open the pod bay doors, HAL?",
            )}
