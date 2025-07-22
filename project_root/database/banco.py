"""
database/banco.py – Cria engine e sessão SQLAlchemy a partir do config.
Inclui função opcional de criação de schema (uso dev). Produção: usar Alembic.
"""

from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports relativos tolerando execução por pacote ou script
try:
    from ..config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE, DEBUG
    from ..models import Base  # Base centralizada em models (você pode manter base.py separado se preferir)
except ImportError:  # execução direta
    from config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE, DEBUG
    from models import Base

# Engine PostgreSQL (ou fallback)
engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,  # verifica conexões mortas
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    """Gerador de sessão para FastAPI / uso manual."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------
# Criação de schema
# -----------------------------------------------------------
def criar_banco_dev():
    """Uso temporário: cria todas as tabelas definidas no metadata."""
    Base.metadata.create_all(bind=engine)
