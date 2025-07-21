# main.py
import sys
import os
import streamlit as st

# ---------------------------------------------------------
# Ajuste de caminho: garante que podemos importar como script
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# ---------------------------------------------------------
# Config inicial de página (antes de qualquer UI)
# ---------------------------------------------------------
st.set_page_config(page_title="Sistema de Compras", layout="wide")

# ---------------------------------------------------------
# Banco / criação de schema
# ---------------------------------------------------------
from banco import criar_banco
criar_banco()

# ---------------------------------------------------------
# Demais módulos
# ---------------------------------------------------------
from auth import login
from views import admin, backlog, cotacao, finalizado, analise, erros

# ---------------------------------------------------------
# Estado de sessão
# ---------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# ---------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------
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
    # elif menu == "Análise":
    #     analise.exibir()
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
