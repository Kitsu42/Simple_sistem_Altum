from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class LogAcao(Base):
    __tablename__ = "logs_acoes"

    id = Column(Integer, primary_key=True)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id"))
    usuario_id = Column(Integer, ForeignKey("users.id"))

    acao = Column(String)
    data = Column(DateTime, default=datetime.utcnow)
    comentario = Column(String, nullable=True)

    requisicao = relationship("RequisicaoCompra", backref="logs")
    usuario = relationship("User")
