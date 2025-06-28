import streamlit as st
from auth import load_authenticator
from database import init_db
from cotacao_page import pagina_cotacao
from relatorios import pagina_relatorios
from relatorio_pdf import pagina_pdf
from upload_nf import pagina_upload
from utils import pagina_principal

import streamlit as st
from auth import load_authenticator
from database import init_db

init_db()
authenticator = load_authenticator()
auth_result = authenticator.login(location="sidebar")

if auth_result is not None:
    name, auth_status, username = auth_result

    if auth_status:
        authenticator.logout("Logout", location="sidebar")
        st.sidebar.success(f"Bem-vindo, {name}")
        # Aqui vai o menu de páginas
        page = st.sidebar.selectbox("Página:", ["Painel Geral", "Cotação", "Relatórios", "Upload", "PDF"])
        # continue a navegação aqui...
    elif auth_status is False:
        st.error("Usuário ou senha incorretos")
    elif auth_status is None:
        st.warning("Insira suas credenciais")
else:
    st.error("Erro ao carregar autenticação.")
