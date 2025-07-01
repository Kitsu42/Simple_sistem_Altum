# login.py
import streamlit as st

USUARIOS = {
    "admin": "admin123",
    "user01": "user01"
}

def autenticar_usuario():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            # Remova o rerun aqui
        else:
            st.error("Usuário ou senha incorretos")
