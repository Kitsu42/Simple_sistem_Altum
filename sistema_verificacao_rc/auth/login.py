# auth/login.py
import streamlit as st
import time
from banco import SessionLocal
from models import Usuario

def exibir():
    st.title("🔐 Login ")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        botao_login = st.form_submit_button("Entrar")

    if botao_login:
        if not usuario_input or not senha_input:
            st.warning("Preencha todos os campos.")
            return

        db = SessionLocal()
        usuario = db.query(Usuario).filter_by(nome=usuario_input, senha=senha_input, ativo=1).first()
        db.close()

        if usuario:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario.nome
            st.session_state.cargo = usuario.cargo
            st.success("Login realizado com sucesso. Redirecionando...")
            time.sleep(1)
            st.session_state.pagina = "Backlog"
        else:
            st.error("Usuário ou senha inválidos ou usuário desativado.")
