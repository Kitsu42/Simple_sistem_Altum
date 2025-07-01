# banco.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///compras.db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def criar_banco():
    from models import Usuario, Requisicao, Item
    Base.metadata.create_all(bind=engine)
