"""
config.py – Carrega variáveis de ambiente e expõe configuração unificada.
Suporta PostgreSQL (preferido) com fallback opcional para SQLite local.
"""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
ROOT_DIR = Path(__file__).resolve().parents[1]  # project_root/
ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# --- Funções helpers ---
def _getenv(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    return val if (val is not None and val != "") else default

# --- DB vars ---
DB_HOST = _getenv("DB_HOST")
DB_PORT = _getenv("DB_PORT", "5432")
DB_NAME = _getenv("DB_NAME")
DB_USER = _getenv("DB_USER")
DB_PASS = _getenv("DB_PASS")

# Fallback SQLite?
DB_FALLBACK_SQLITE = _getenv("DB_FALLBACK_SQLITE", "0") in ("1", "true", "True")

def build_database_url() -> str:
    """Retorna URL SQLAlchemy para PostgreSQL ou fallback SQLite."""
    if all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    if DB_FALLBACK_SQLITE:
        return f"sqlite:///{ROOT_DIR / 'banco.db'}"
    raise RuntimeError("Variáveis de DB PostgreSQL ausentes e fallback SQLite desabilitado.")

DATABASE_URL = build_database_url()

# Pool config
DB_POOL_SIZE = int(_getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(_getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_RECYCLE = int(_getenv("DB_POOL_RECYCLE", "1800"))  # 30 min

# App settings futuros...
DEBUG = _getenv("DEBUG", "0") in ("1", "true", "True")
