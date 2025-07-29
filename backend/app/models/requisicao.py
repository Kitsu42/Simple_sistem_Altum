from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class RequisicaoCompra(Base):
    __tablename__ = "requisicoes"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True)
    empresa = Column(String)
    filial = Column(String)
    urgencia = Column(Boolean, default=False)
    status = Column(String, default="pendente")

    operador_id = Column(Integer, ForeignKey("users.id"))
    operador = relationship("User")

    nota = Column(String, nullable=True)
    data_cotacao = Column(Date, nullable=True)
    data_aprovacao = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    data_recebimento = Column(Date, nullable=True)
