# main.py
import streamlit as st
from login import autenticar_usuario
from views import backlog, cotacao, finalizado

st.set_page_config(page_title="Sistema de Compras", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    autenticar_usuario()
else:
    menu = st.sidebar.selectbox("Navegar", ["Backlog", "Em Cotação", "Finalizado"])

    if menu == "Backlog":
        backlog.exibir()
    elif menu == "Em Cotação":
        cotacao.exibir()
    elif menu == "Finalizado":
        finalizado.exibir()

    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"autenticado": False}))
