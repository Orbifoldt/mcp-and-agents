from fastapi import FastAPI

from app.openai_client import get_openai_client
from common.settings import get_settings

app = FastAPI()

@app.get("/")
async def read_root():
    settings = get_settings()
    llm = get_openai_client()
    result = llm.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": "Hello, world!"}],
        model=settings.gpt_5_6_luna.deployment_name
    )
    return {"Hello": "World", "Settings": settings.dict(),
            "msg": result}


