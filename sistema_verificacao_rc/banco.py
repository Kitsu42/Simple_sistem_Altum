from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Usuario, Requisicao, Item

engine = create_engine("sqlite:///compras.db")
SessionLocal = sessionmaker(bind=engine)

def criar_banco():
    Base.metadata.create_all(bind=engine)