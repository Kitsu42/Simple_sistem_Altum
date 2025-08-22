from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from app.core.db import Base

class Empresa(Base):
    __tablename__ = "empresas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    cnpj: Mapped[str | None] = mapped_column(String(20), unique=True)

class Filial(Base):
    __tablename__ = "filiais"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), index=True)
    nome: Mapped[str] = mapped_column(String(150))
    cnpj: Mapped[str | None] = mapped_column(String(20))
