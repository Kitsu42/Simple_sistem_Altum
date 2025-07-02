# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from banco import Base
from sqlalchemy import Column, Integer, String, Date

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
    link = Column(String, default="")  # ✅ ADICIONE ESTA LINHA

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    senha = Column(String)

class Requisicao(Base):
    __tablename__ = "requisicoes"
    id = Column(Integer, primary_key=True)
    numero_sc = Column(String)
    data = Column(Date)
    empresa = Column(String)
    filial = Column(String)
    status = Column(String)
    responsavel = Column(String)

class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    quantidade = Column(Integer)
    codigo_erp = Column(String)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id"))