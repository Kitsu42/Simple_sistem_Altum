# login.py
#import streamlit as st

#USUARIOS = {
#    "admin": {"senha": "admin123", "cargo": "admin"},
#    "user01": {"senha": "user01", "cargo": "comprador"},
#    "gilmar": {"senha": "gilmar262", "cargo": "comprador"},
#    "kamilla": {"senha": "senha", "cargo": "comprador"},
#    "valeria": {"senha": "senha", "cargo": "comprador"},
#    "kaio": {"senha": "senha", "cargo": "comprador"},
#    "alice": {"senha": "senha", "cargo": "comprador"},
#    "luiz": {"senha": "senha", "cargo": "comprador"},
}

#def autenticar_usuario():
#    st.title("Login")
#   usuario = st.text_input("Usuário")
#   senha = st.text_input("Senha", type="password")
#
#    if st.button("Entrar"):
#        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
#            st.session_state["autenticado"] = True
#            st.session_state["usuario"] = usuario
#            st.session_state["cargo"] = USUARIOS[usuario]["cargo"]
#        else:
#            st.error("Usuário ou senha incorretos")
