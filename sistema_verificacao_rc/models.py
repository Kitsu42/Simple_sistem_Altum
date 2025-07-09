# models.py
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from base import Base  # Agora importa corretamente

class Requisicao(Base):
    __tablename__ = "requisicoes"
    id = Column(Integer, primary_key=True, index=True)
    rc = Column(String)
    solicitacao_senior = Column(String)
    empresa = Column(String)
    filial = Column(String)
    data = Column(Date)
    status = Column(String)
    responsavel = Column(String)
    link = Column(Text)
    numero_oc = Column(String)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    ativo = Column(Integer, default=1)

class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    quantidade = Column(Integer)
    codigo_erp = Column(String)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id"))
