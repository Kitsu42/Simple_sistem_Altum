from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Enum
import enum


class StatusRequisicao(enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    aprovado = "aprovado"
    recusado = "recusado"

class RequisicaoCompra(Base):
    __tablename__ = "requisicoes"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True)
    empresa = Column(String)
    filial = Column(String)
    urgencia = Column(Boolean, default=False)
    status = Column(Enum(StatusRequisicao), default=StatusRequisicao.pendente)
    logs = relationship("LogAcao", back_populates="requisicao")

    operador_id = Column(Integer, ForeignKey("users.id"), index=True)
    operador = relationship("User")

    nota = Column(String, nullable=True)
    data_cotacao = Column(Date, nullable=True)
    data_aprovacao = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    data_recebimento = Column(Date, nullable=True)

    def __repr__(self):
        return f"<RequisicaoCompra(codigo={self.codigo}, status={self.status})>"
