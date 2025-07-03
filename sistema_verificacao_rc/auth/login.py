# auth/login.py
import streamlit as st
import time

USUARIOS = {
    "admin": {"senha": "admin123", "cargo": "admin"},
    "user01": {"senha": "user01", "cargo": "comprador"},
    "gilmar": {"senha": "gilmar262", "cargo": "comprador"},
    "kamilla": {"senha": "senha", "cargo": "comprador"},
    "valeria": {"senha": "senha", "cargo": "comprador"},
    "kaio": {"senha": "senha", "cargo": "comprador"},
    "alice": {"senha": "senha", "cargo": "comprador"},
    "luiz": {"senha": "senha", "cargo": "comprador"},
}

def exibir():
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Login - Sistema de Compras")

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        login = st.form_submit_button("Entrar")

    if login:
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.cargo = USUARIOS[usuario]["cargo"]
            st.success("Login realizado com sucesso. Redirecionando...")

            # Pausa para que o usuário veja a mensagem antes de redirecionar
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
