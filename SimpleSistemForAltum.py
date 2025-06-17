import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

st.set_page_config(page_title="Auxiliar de idiotas", layout="wide")
st.title("Organizador de RC")

DB_ARQUIVO = "historico_rc.csv"

# Carregar histórico se existir
if os.path.exists(DB_ARQUIVO):
    historico_df = pd.read_csv(DB_ARQUIVO)
else:
    historico_df = pd.DataFrame(columns=['Nº SC', 'DATA SC', 'OBSERVAÇÃO', 'Qtd Linhas', 'Responsável'])

uploaded_file = st.file_uploader("Faça upload de uma planilha Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    selected_sheet = st.selectbox("Escolha a aba da planilha:", sheet_names)

    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    col_necessarias = ['Nº SC', 'DATA SC', 'OBSERVAÇÃO']
    if not all(col in df.columns for col in col_necessarias):
        st.error("A planilha precisa conter as colunas: 'Nº SC', 'DATA SC', 'OBSERVAÇÃO'")
        st.stop()

    df['Nº SC'] = df['Nº SC'].astype(str)
    df['DATA SC'] = pd.to_datetime(df['DATA SC'], errors='coerce')
    df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].fillna('')

    agrupado = df.groupby('Nº SC').agg({
        'DATA SC': 'first',
        'OBSERVAÇÃO': 'first',
        'Nº SC': 'count'
    }).rename(columns={'Nº SC': 'Qtd Linhas'}).reset_index()

    st.markdown("### Requisições encontradas:")

    novos_registros = []

    for _, row in agrupado.iterrows():
        numero_sc = row['Nº SC']
        data_sc = row['DATA SC']
        observacao = row['OBSERVAÇÃO']
        qtd_linhas = row['Qtd Linhas']

        # Ver se já existe no histórico
        if numero_sc in historico_df['Nº SC'].values:
            responsavel = historico_df[historico_df['Nº SC'] == numero_sc]['Responsável'].values[0]
        else:
            responsavel = st.text_input(f"Quem está cuidando da SC {numero_sc}?", key=numero_sc)

        tempo_aberto = "—"
        if pd.notnull(data_sc):
            delta = relativedelta(datetime.now(), data_sc)
            tempo_aberto = f"{delta.years}a {delta.months}m {delta.days}d"

        link = observacao if "http" in observacao else "#"

        st.markdown(
            f"""
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                <h4> Nº SC: {numero_sc}</h4>
                <p><strong>Data SC:</strong> {data_sc.strftime('%d/%m/%Y') if pd.notnull(data_sc) else '—'}</p>
                <p><strong>Tempo aberto:</strong> {tempo_aberto}</p>
                <p><strong>Qtd Linhas:</strong> {qtd_linhas}</p>
                <p><strong>Responsável:</strong> {responsavel or '—'}</p>
                <a href="{link}" target="_blank">🔗 Acessar painel</a>
            </div>
            """,
            unsafe_allow_html=True
        )

        if responsavel and numero_sc not in historico_df['Nº SC'].values:
            novos_registros.append({
                'Nº SC': numero_sc,
                'DATA SC': data_sc,
                'OBSERVAÇÃO': observacao,
                'Qtd Linhas': qtd_linhas,
                'Responsável': responsavel
            })

    # Atualizar histórico
    if novos_registros:
        novos_df = pd.DataFrame(novos_registros)
        historico_df = pd.concat([historico_df, novos_df], ignore_index=True)
        historico_df.to_csv(DB_ARQUIVO, index=False)
        st.success("Histórico atualizado com sucesso!")

    # Exportar relatório completo
    if not historico_df.empty:
        st.markdown("---")
        st.markdown("###Relatório Histórico")
        st.dataframe(historico_df)

        csv = historico_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar relatório CSV",
            data=csv,
            file_name='relatorio_RC.csv',
            mime='text/csv',
        )
