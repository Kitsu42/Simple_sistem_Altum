"""
init_db.py
----------
Cria as tabelas no banco com base nos models.
"""

from banco import engine
from models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Banco de dados inicializado com sucesso.")

if __name__ == "__main__":
    init_db()
