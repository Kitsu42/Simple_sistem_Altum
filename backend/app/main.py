from fastapi import FastAPI
from app.core.database import engine
from app.models import base, user, requisicao, log

from app.routers import example  # caso você esteja incluindo esse router

app = FastAPI(title="Sistema de Compras", version="0.1.0")

base.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Sistema de Compras pronto!"}

app.include_router(example.router)
