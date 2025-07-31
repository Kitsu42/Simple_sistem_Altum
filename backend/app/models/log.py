from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class LogAcao(Base):
    __tablename__ = "logs_acoes"

    id = Column(Integer, primary_key=True)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id"), index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), index=True)

    acao = Column(String, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)
    comentario = Column(String, nullable=True)

    requisicao = relationship("RequisicaoCompra", backref="logs")
    usuario = relationship("User")

    def __repr__(self):
        return f"<LogAcao(requisicao_id={self.requisicao_id}, usuario_id={self.usuario_id}, acao={self.acao}, data={self.data})>"
