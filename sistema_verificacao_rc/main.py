# main.py
import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(__file__))

from views import admin
from auth import login
from views import backlog, cotacao, finalizado, analise, erros
from banco import criar_banco

st.set_page_config(page_title="Sistema de Compras", layout="wide")

criar_banco()

# Inicializa variáveis da sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# Verifica se usuário está autenticado
if not st.session_state.autenticado:
    login.exibir()
else:
    # Exibe menu lateral com ou sem Admin, dependendo do cargo
    if st.session_state.cargo == "admin":
        menu = st.sidebar.radio("Menu", ("Backlog", "Em Cotação", "Finalizado", "Análise", "Erros", "Admin"))
    else:
        menu = st.sidebar.radio("Menu", ("Backlog", "Em Cotação", "Finalizado", "Análise", "Erros"))

    # Direciona para a view correta
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
    elif menu == "Admin":
        admin.exibir()
