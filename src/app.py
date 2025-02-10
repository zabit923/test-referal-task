import logging

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from admin import (
    AdminAuth,
    UserAdmin,
)
from api.routers import router as api_router
from config import settings
from core.database.db import engine
from core.security.jwt import HTTPAuthenticationMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=HTTPAuthenticationMiddleware())

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )