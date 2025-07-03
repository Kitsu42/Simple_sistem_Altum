# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from base import Base 

class Requisicao(Base):
    __tablename__ = "requisicoes"
    id = Column(Integer, primary_key=True, index=True)
    numero_sc = Column(String, index=True)
    data = Column(Date)
    empresa = Column(String)
    filial = Column(String)
    responsavel = Column(String, default="")
    status = Column(String)
    numero_oc = Column(String, default="")
    link = Column(String, default="")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    senha = Column(String)
    cargo = Column(String)  # admin, comprador, etc.
    ativo = Column(Integer, default=1)  # 1 = ativo, 0 = desativado

class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    quantidade = Column(Integer)
    codigo_erp = Column(String)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id"))
