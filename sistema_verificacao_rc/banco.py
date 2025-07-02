from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

engine = create_engine("sqlite:///compras.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Importar modelos aqui, para registrar as classes de tabela
from models import Usuario, Requisicao, Item

def criar_banco():
    Base.metadata.create_all(bind=engine)
