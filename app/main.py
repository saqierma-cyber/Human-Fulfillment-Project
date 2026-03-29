from fastapi import FastAPI

from app.api.routes_admin import router as admin_router
from app.api.routes_chat import router as chat_router
from app.core.config import get_settings
from app.db.session import init_db


settings = get_settings()

app = FastAPI(title=settings.app_name)

init_db()

app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "status": "ok",
        "env": settings.app_env,
    }
