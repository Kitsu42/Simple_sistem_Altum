import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auxiliar de idiotas", layout="wide")
st.title("Organizador de RC")

uploaded_file = st.file_uploader("Faça upload de uma planilha Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    selected_sheet = st.selectbox("Escolha a aba da planilha:", sheet_names)

    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    # Verifica se as colunas esperadas existem
    col_necessarias = ['Nº SC', 'DATA SC', 'OBSERVAÇÃO']
    if not all(col in df.columns for col in col_necessarias):
        st.error("A planilha precisa conter as colunas: 'Nº SC', 'DATA SC', 'OBSERVAÇÃO'")
        st.stop()

    # Limpar e preparar
    df['Nº SC'] = df['Nº SC'].astype(str)
    df['DATA SC'] = pd.to_datetime(df['DATA SC'], errors='coerce')
    df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].fillna('')

    # Agrupar por Nº SC
    agrupado = df.groupby('Nº SC').agg({
        'DATA SC': 'first',
        'OBSERVAÇÃO': 'first',
        'Nº SC': 'count'
    }).rename(columns={'Nº SC': 'Qtd Linhas'}).reset_index()

    # Exibir cards
    st.markdown("###Resultados encontrados:")
    for _, row in agrupado.iterrows():
        link = row['OBSERVAÇÃO'] if "http" in str(row['OBSERVAÇÃO']) else "#"
        st.markdown(
            f"""
            <div style='background-color: #f0f0f5; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                <h4> Nº SC: {row['Nº SC']}</h4>
                <p><strong>Data SC:</strong> {row['DATA SC'].strftime('%d/%m/%Y') if pd.notnull(row['DATA SC']) else '—'}</p>
                <p><strong>Qtd Linhas:</strong> {row['Qtd Linhas']}</p>
                <a href="{link}" target="_blank">🔗 Acessar painel</a>
            </div>
            """,
            unsafe_allow_html=True
        )
