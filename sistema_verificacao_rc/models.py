from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Empresa(Base):
    __tablename__ = \"empresas\"
    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, index=True)   # Ex: '5SS'
    nome = Column(String, nullable=False)              # Razão social completa
    filiais = relationship(\"Filial\", back_populates=\"empresa\", cascade=\"all, delete-orphan\")


class Filial(Base):
    __tablename__ = \"filiais\"
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey(\"empresas.id\"), nullable=False)
    codigo = Column(String, index=True)                # Ex: '5SS-1'
    cnpj = Column(String, index=True)
    cidade = Column(String)
    nome_exibicao = Column(String)                     # Ex: '5SS-1 - Aparecida'

    empresa = relationship(\"Empresa\", back_populates=\"filiais\")
    requisicoes = relationship(\"Requisicao\", back_populates=\"filial_obj\")


class Requisicao(Base):
    __tablename__ = \"requisicoes\"
    id = Column(Integer, primary_key=True, index=True)
    rc = Column(String)
    solicitacao_senior = Column(String)

    # Campos legado (nomes das colunas originais preservados)
    empresa_txt = Column(\"empresa\", String)
    filial_txt = Column(\"filial\", String)

    data = Column(Date)
    status = Column(String)
    responsavel = Column(String)
    link = Column(Text)
    numero_oc = Column(String)

    # Novo relacionamento normalizado
    filial_id = Column(Integer, ForeignKey(\"filiais.id\"), nullable=True)
    filial_obj = relationship(\"Filial\", back_populates=\"requisicoes\")

    # Conveniência p/ exibir nomes padronizados mesmo sem migrar tudo
    @property
    def empresa_display(self):
        try:
            if self.filial_obj and self.filial_obj.empresa:
                return self.filial_obj.empresa.nome
        except Exception:
            pass
        return self.empresa_txt

    @property
    def filial_display(self):
        try:
            if self.filial_obj:
                return self.filial_obj.nome_exibicao or self.filial_obj.cidade
        except Exception:
            pass
        return self.filial_txt


class Usuario(Base):
    __tablename__ = \"usuarios\"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)  # TODO: hash
    cargo = Column(String, nullable=False)
    ativo = Column(Integer, default=1)


class Item(Base):
    __tablename__ = \"itens\"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    quantidade = Column(Integer)
    codigo_erp = Column(String)
    requisicao_id = Column(Integer, ForeignKey(\"requisicoes.id\"))