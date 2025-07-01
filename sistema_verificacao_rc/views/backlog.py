# views/backlog.py
import streamlit as st
from planilhas import carregar_backlog
import pandas as pd

def exibir():
    st.title("Backlog de SCs")
    arquivo = st.file_uploader("Enviar planilha de backlog", type="xlsx")
    if arquivo:
        df = carregar_backlog(arquivo)

        # Preencher coluna 'Dias em aberto' se necessário
        if 'DATA SC' in df.columns:
            df['Dias em aberto'] = pd.to_datetime("today") - pd.to_datetime(df['DATA SC'], errors='coerce')
            df['Dias em aberto'] = df['Dias em aberto'].dt.days

        # Agrupar por SC única
        agrupado = df.groupby(['Nº SC', 'Empresa', 'Filial']).agg({
            'DATA SC': 'first',
            'Dias em aberto': 'min',
            'DESCRICAO': 'count'  # quantidade de itens
        }).reset_index()

        for i, row in agrupado.iterrows():
            with st.expander(f"SC {row['Nº SC']} | {row['Empresa']} - {row['Filial']}"):
                st.write(f"Quantidade de Itens: {row['DESCRICAO']}")
                st.write(f"Data de criação: {row['DATA SC']}")
                st.write(f"Dias em aberto: {row['Dias em aberto']}")
                if st.button("Iniciar Cotação", key=f"cotacao_{row['Nº SC']}_{i}"):
                    # Aqui você pode salvar no banco com status 'em cotação'
                    st.success("Cotação iniciada")