import streamlit as st
import pandas as pd
from datetime import datetime
from models import RC
from database import SessionLocal

def load_backlog(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

def separar_rcs(df):
    rcs = []
    hoje = datetime.today()
    for _, row in df.iterrows():
        data_criacao = pd.to_datetime(row["Data SC"], dayfirst=True)
        dias = (hoje - data_criacao).days
        rcs.append({
            "numero_sc": row["Nº SC"],
            "data": data_criacao.strftime("%d/%m/%Y"),
            "dias_aberto": dias,
            "qtd_itens": row["Qtd Itens"],
            "empresa": row["Empresa"],
            "filial": row["Filial"]
        })
    return rcs

def salvar_rcs_no_banco(rcs, db):
    for rc in rcs:
        if not db.query(RC).filter_by(numero_sc=rc["numero_sc"]).first():
            nova = RC(
                numero_sc=rc["numero_sc"],
                data_criacao=datetime.strptime(rc["data"], "%d/%m/%Y"),
                dias_aberto=rc["dias_aberto"],
                qtd_itens=rc["qtd_itens"],
                empresa=rc["empresa"],
                filial=rc["filial"]
            )
            db.add(nova)
    db.commit()

def pagina_principal():
    st.title("📊 Painel de RCs")
    uploaded_file = st.file_uploader("Enviar planilha .xlsx", type=["xlsx"])
    db = SessionLocal()
    if uploaded_file:
        df = load_backlog(uploaded_file)
        rcs = separar_rcs(df)
        salvar_rcs_no_banco(rcs, db)
        st.success("Planilha processada.")
    status_filtro = st.selectbox("Filtrar por status", ["aberta", "cotação", "concluída"])
    rcs = db.query(RC).filter(RC.status == status_filtro).all()
    for rc in rcs:
        with st.expander(f"SC {rc.numero_sc}"):
            st.markdown(f"- Criada: {rc.data_criacao.strftime('%d/%m/%Y')}")
            novo_resp = st.text_input("Responsável", rc.responsavel or "", key=f"r{rc.id}")
            novo_status = st.selectbox("Status", ["aberta", "cotação", "concluída"], index=["aberta", "cotação", "concluída"].index(rc.status), key=f"s{rc.id}")
            numero_oc = st.text_input("Nº OC", rc.numero_oc or "", key=f"o{rc.id}")
            if st.button("Salvar", key=f"b{rc.id}"):
                rc.responsavel = novo_resp
                if novo_status == "concluída" and not numero_oc.strip():
                    st.error("Nº OC obrigatório para concluir.")
                else:
                    rc.status = novo_status
                    rc.numero_oc = numero_oc.strip()
                    db.commit()
                    st.success("Atualizado com sucesso.")
    db.close()
