# planilhas.py
import pandas as pd

def carregar_backlog(caminho_excel: str) -> pd.DataFrame:
    xls = pd.ExcelFile(caminho_excel)
    dados = []
    for aba in xls.sheet_names:
        df = xls.parse(aba)
        df["Origem"] = aba
        df["Empresa"] = df.get("Empresa 2", "")
        df["Filial"] = df.get("FILIAL", "")
        dados.append(df)
    return pd.concat(dados, ignore_index=True)
