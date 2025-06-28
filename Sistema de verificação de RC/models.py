from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from database import Base
from datetime import datetime

class RC(Base):
    __tablename__ = "rcs"

    id = Column(Integer, primary_key=True)
    numero_sc = Column(String, unique=True, index=True)
    data_criacao = Column(Date)
    dias_aberto = Column(Integer)
    filial = Column(String)
    empresa = Column(String)
    qtd_itens = Column(Integer)
    status = Column(String, default="aberta")
    responsavel = Column(String, nullable=True)
    numero_oc = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.now)

    fornecedor_nome = Column(String, nullable=True)
    fornecedor_telefone = Column(String, nullable=True)
    fornecedor_empresa = Column(String, nullable=True)

    lembrete_nf = Column(Boolean, default=False)
    lembrete_cobrar = Column(Boolean, default=False)
    lembrete_oc = Column(Boolean, default=False)
