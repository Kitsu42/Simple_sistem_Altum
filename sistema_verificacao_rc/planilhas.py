# planilhas.py
import pandas as pd

def carregar_backlog(caminho_excel: str) -> pd.DataFrame:
    xls = pd.ExcelFile(caminho_excel)
    dados = []

    for aba in xls.sheet_names:
        df = xls.parse(aba)
        df["Origem"] = aba

        # Normaliza campos esperados
        if "Empresa" not in df.columns:
            df["Empresa"] = ""
        if "Filial" not in df.columns:
            df["Filial"] = ""
        if "RC" not in df.columns:
            df["RC"] = ""
        if "Solicitacao Senior" not in df.columns:
            df["Solicitacao Senior"] = ""
        if "Data Cadastro" not in df.columns:
            df["Data Cadastro"] = pd.NaT
        if "Link" not in df.columns:
            df["Link"] = ""

        # Converte 'Data Cadastro' para datetime.date se existir
        if "Data Cadastro" in df.columns:
            df["Data Cadastro"] = pd.to_datetime(df["Data Cadastro"], errors="coerce").dt.date

        dados.append(df)

    return pd.concat(dados, ignore_index=True)