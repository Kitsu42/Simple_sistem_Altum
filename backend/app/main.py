from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base, engine
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.rcs import router as rcs_router

app = FastAPI(title=settings.APP_NAME)

# CORS
origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria tabelas automaticamente em dev (migrations virão depois)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Rotas
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(rcs_router, prefix="/api/v1/rcs", tags=["rcs"])

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
