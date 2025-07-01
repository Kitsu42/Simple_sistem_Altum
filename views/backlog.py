# views/backlog.py
import streamlit as st
import pandas as pd
from planilhas import carregar_backlog

def exibir():
    st.title("Backlog de SCs")
    arquivo = st.file_uploader("Enviar planilha de backlog", type="xlsx")
    if arquivo:
        df = carregar_backlog(arquivo)
        for _, row in df.iterrows():
            with st.expander(f"SC: {row['Nº SC']} | {row['Empresa']} - {row['Filial']}"):
                st.write("Descrição:", row["DESCRICAO"])
                st.write("Quantidade:", row["QUANTIDADE"])
                st.write("Data SC:", row["DATA SC"])
                st.write("Dias em aberto:", row["Dias em aberto"])
                st.write("Origem:", row["Origem"])
                st.button("Iniciar Cotação", key=str(row["Nº SC"]))
