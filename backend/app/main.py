from fastapi import FastAPI
from app.core.database import engine
from app.models import base, user, requisicao, log  # garante que as tabelas sejam registradas

app = FastAPI(title="Sistema de Compras", version="0.1.0")

# Cria as tabelas no banco apenas se ainda não existem (modo dev)
base.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Sistema de Compras pronto!"}
