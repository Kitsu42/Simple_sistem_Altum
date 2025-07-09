# main.py
import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(__file__))

from banco import criar_banco

# Cria banco e tabelas ANTES de qualquer outra coisa
criar_banco()

# Agora sim pode importar os módulos que dependem do banco
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
        menu = st.sidebar.radio("Menu", ("Backlog", "Em Cotação", "Finalizado", "Análise", "Erros", "Admin"))
    else:
        menu = st.sidebar.radio("Menu", ("Backlog", "Em Cotação", "Finalizado", "Análise", "Erros"))

    if menu == "Backlog":
        backlog.exibir()
    elif menu == "Em Cotação":
        cotacao.exibir()
    elif menu == "Análise":
        analise.exibir()
    elif menu == "Finalizado":
        finalizado.exibir()
    elif menu == "Erros":
        erros.exibir()
    elif menu == "Admin":
        admin.exibir()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.cargo = None
        st.session_state.pagina = "Backlog"