# views/gerar_xml.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Requisicao, Usuario, Item

def exibir():
    st.title("📤 Exportação de Dados do Sistema")

    db = SessionLocal()

    st.subheader("📋 Exportar Requisições (RCs)")
    requisicoes = db.query(Requisicao).all()
    df_rcs = pd.DataFrame([{
        "id": r.id,
        "rc": r.rc,
        "solicitacao_senior": r.solicitacao_senior,
        "empresa": r.empresa,
        "filial": r.filial,
        "data": r.data,
        "status": r.status,
        "responsavel": r.responsavel,
        "link": r.link,
        "numero_oc": r.numero_oc
    } for r in requisicoes])
    st.download_button("📥 Baixar RCs em CSV", df_rcs.to_csv(index=False), file_name="requisicoes.csv", mime="text/csv")

    st.subheader("👤 Exportar Usuários")
    usuarios = db.query(Usuario).all()
    df_users = pd.DataFrame([{
        "id": u.id,
        "nome": u.nome,
        "senha": u.senha,
        "cargo": u.cargo,
        "ativo": u.ativo
    } for u in usuarios])
    st.download_button("📥 Baixar Usuários em CSV", df_users.to_csv(index=False), file_name="usuarios.csv", mime="text/csv")

    st.subheader("📦 Exportar Itens de RCs")
    itens = db.query(Item).all()
    df_itens = pd.DataFrame([{
        "id": i.id,
        "descricao": i.descricao,
        "quantidade": i.quantidade,
        "codigo_erp": i.codigo_erp,
        "requisicao_id": i.requisicao_id
    } for i in itens])
    st.download_button("📥 Baixar Itens em CSV", df_itens.to_csv(index=False), file_name="itens.csv", mime="text/csv")

    db.close()
