from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Usuario, Requisicao, Item

engine = create_engine("sqlite:///compras.db")
SessionLocal = sessionmaker(bind=engine)

def criar_banco():
    Base.metadata.create_all(bind=engine)

def popular_usuarios_iniciais():
    session = SessionLocal()
    if session.query(Usuario).count() == 0:
        usuarios_iniciais = [
            Usuario(nome="admin", senha="admin123", cargo="admin"),
            Usuario(nome="user01", senha="user01", cargo="comprador"),
        ]
        session.add_all(usuarios_iniciais)
        session.commit()
    session.close()

def criar_banco():
    Base.metadata.create_all(bind=engine)
    popular_usuarios_iniciais()

