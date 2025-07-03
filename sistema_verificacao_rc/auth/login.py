# login.py
import streamlit as st
from banco import SessionLocal
from models import Usuario

def exibir():
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Login ")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        login = st.form_submit_button("Entrar")

    if login:
        if not usuario_input or not senha_input:
            st.warning("Preencha todos os campos.")
            return

        db = SessionLocal()
        try:
            usuario = (
                db.query(Usuario)
                .filter_by(nome=usuario_input, senha=senha_input, ativo=True)
                .first()
            )
        finally:
            db.close()

        if usuario:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario.nome
            st.session_state.cargo = usuario.cargo
            st.success(f"Bem-vindo, {usuario.nome}. Redirecionando...")
        st.session_state.pagina = "Backlog"
        else:
            st.error("Usuário ou senha inválidos, ou usuário desativado.")
