# main.py
import streamlit as st
from auth import login
from views import backlog, cotacao, finalizado, analise, erros
from banco import criar_banco

st.set_page_config(page_title="Sistema de Compras", layout="wide")

criar_banco()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "cargo" not in st.session_state:
    st.session_state.cargo = None

if not st.session_state.autenticado:
    login.exibir()
else:
    menu = st.sidebar.radio("Menu", ("Backlog", "Em Cotação", "Finalizado", "Análise", "Erros"))

    if menu == "Backlog":
        backlog.exibir()
    elif menu == "Em Cotação":
        cotacao.exibir()
    elif menu == "Finalizado":
        finalizado.exibir()
    elif menu == "Análise":
        analise.exibir()
    elif menu == "Erros":
        erros.exibir()