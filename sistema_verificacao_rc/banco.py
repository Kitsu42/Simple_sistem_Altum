# banco.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import models
from models import Usuario

engine = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def popular_usuarios_iniciais():
    session = SessionLocal()
    try:
        if session.query(Usuario).count() == 0:
            session.add_all([
                Usuario(nome="admin", senha="admin123", cargo="admin"),
                Usuario(nome="user01", senha="user01", cargo="comprador"),
            ])
            session.commit()
    except Exception as e:
        print(f"[ERRO ao popular usuários iniciais]: {e}")
    finally:
        session.close()

def criar_banco():
    print("👉 Criando banco...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estrutura criada.")
    popular_usuarios_iniciais()
