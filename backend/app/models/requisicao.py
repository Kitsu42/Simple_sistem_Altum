from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey, func
from app.core.db import Base
import enum

class StatusRC(str, enum.Enum):
    nova = "nova"
    em_cotacao = "em_cotacao"
    aguardando_oc = "aguardando_oc"
    aguardando_nf = "aguardando_nf"
    para_pagamento = "para_pagamento"
    concluida = "concluida"
    cancelada = "cancelada"

class Requisicao(Base):
    __tablename__ = "requisicoes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rc_numero: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    ns_numero: Mapped[str | None] = mapped_column(String(50), index=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), index=True)
    filial_id: Mapped[int] = mapped_column(ForeignKey("filiais.id"), index=True)
    solicitante: Mapped[str | None] = mapped_column(String(120))
    observacoes: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[StatusRC] = mapped_column(Enum(StatusRC), default=StatusRC.nova, index=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
