# main.py
import sys
import os
import streamlit as st

# Garante que o diretório raiz do projeto esteja no sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from banco import criar_banco

criar_banco()

from views import admin
from auth import login
from views import backlog, cotacao, finalizado, analise, erros

st.set_page_config(page_title="Sistema de Compras", layout="wide")

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
    if st.session_state.cargo == "admin":
        menu = st.sidebar.radio("Menu", ("Backlog", "Cotação", "Finalizado", "Erros", "Admin"))
    else:
        menu = st.sidebar.radio("Menu", ("Backlog", "Cotação", "Finalizado", "Erros"))

    if menu == "Backlog":
        backlog.exibir()
    elif menu == "Cotação":
        cotacao.exibir()
    #elif menu == "Análise":
        #analise.exibir()
    elif menu == "Finalizado":
        finalizado.exibir()
    elif menu == "Erros":
        erros.exibir()
        
    elif menu == "Admin":
        admin.exibir()

    st.sidebar.markdown("---")
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.cargo = None
        st.session_state.pagina = "Backlog"