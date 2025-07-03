# views/admin.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Usuario, Requisicao
from sqlalchemy import func
from datetime import datetime, timedelta


def exibir():
    if st.session_state.get("cargo") != "admin":
        st.error("Acesso restrito.")
        return

    st.title("👥 Administração do Sistema")
    db = SessionLocal()

    st.header("📊 Relatórios e Produtividade")

    # Filtro de datas para relatório
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", datetime.today() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data final", datetime.today())

    # Consulta dados no intervalo
    requisicoes = db.query(Requisicao).filter(Requisicao.data >= data_inicio, Requisicao.data <= data_fim).all()
    df = pd.DataFrame([{
        "usuario": r.responsavel,
        "data": r.data,
        "status": r.status,
        "empresa": r.empresa,
        "filial": r.filial
    } for r in requisicoes if r.responsavel])

    if df.empty:
        st.info("Nenhuma requisição registrada no período.")
    else:
        st.subheader("📈 RCs por usuário e status")
        prod = df.groupby(["usuario", "status"]).size().unstack(fill_value=0)
        st.dataframe(prod)

        st.subheader("📅 RCs criadas por dia")
        por_data = df.groupby("data").size()
        st.line_chart(por_data)

        st.subheader("🧾 Total de RCs por usuário no período")
        total = df.groupby("usuario").size().sort_values(ascending=False)
        st.bar_chart(total)

        st.subheader("📍 RCs em cotação por usuário")
        em_cotacao = df[df.status == "em cotação"].groupby("usuario").size()
        st.dataframe(em_cotacao)

        st.subheader("⏱️ RCs atrasadas por usuário")
        dias = (pd.to_datetime("today") - df["data"]).dt.days
        df["dias"] = dias
        atrasadas = df[(df["status"] == "em cotação") & (df["dias"] > 7)]  # Considera atraso > 7 dias
        atrasadas_por_user = atrasadas.groupby("usuario").size()
        st.dataframe(atrasadas_por_user)

    st.markdown("---")
    st.header("👤 Gerenciamento de Usuários")

    # --- Formulário de cadastro ---
    with st.form("form_novo_usuario"):
        nome = st.text_input("Nome de usuário")
        senha = st.text_input("Senha")
        cargo = st.selectbox("Cargo", ["comprador", "admin"])
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            existente = db.query(Usuario).filter_by(nome=nome).first()
            if existente:
                st.warning("Este nome de usuário já está em uso.")
            else:
                novo = Usuario(nome=nome, senha=senha, cargo=cargo, ativo=1)
                db.add(novo)
                db.commit()
                st.success("Usuário cadastrado com sucesso.")
                st.experimental_rerun()

    usuarios = db.query(Usuario).all()
    for u in usuarios:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.write(f"**{u.nome}**")
        with col2:
            st.write(u.cargo)
        with col3:
            status = "✅ Ativo" if u.ativo else "❌ Inativo"
            st.write(status)
        with col4:
            if u.ativo:
                if st.button("Desativar", key=f"desativar_{u.id}"):
                    u.ativo = 0
                    db.commit()
                    st.experimental_rerun()
            else:
                if st.button("Ativar", key=f"ativar_{u.id}"):
                    u.ativo = 1
                    db.commit()
                    st.experimental_rerun()
        with col5:
            if st.button("Excluir", key=f"excluir_{u.id}"):
                db.delete(u)
                db.commit()
                st.experimental_rerun()

    db.close()
