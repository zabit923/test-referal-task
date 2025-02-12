import logging

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware

from admin import AdminAuth, RefferalAdmin, RefferalCodeAdmin, UserAdmin
from api.routers import router as api_router
from config import redis_client, settings
from core.database.db import engine

logging.basicConfig(
    format=settings.logging.log_format,
)


origins = ["http://localhost:8000", "http://localhost:5173", "ws://127.0.0.1:8000"]


app = FastAPI()
app.include_router(
    api_router,
)

admin_auth = AdminAuth(secret_key=settings.secret.secret_key)
admin = Admin(app=app, engine=engine, authentication_backend=admin_auth)
admin.add_view(UserAdmin)
admin.add_view(RefferalCodeAdmin)
admin.add_view(RefferalAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def shutdown_event():
    await redis_client.aclose()


app.add_event_handler("shutdown", shutdown_event)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
