# planilhas.py
import pandas as pd

def carregar_backlog(caminho_excel: str) -> pd.DataFrame:
    xls = pd.ExcelFile(caminho_excel)
    dados = []
    for aba in xls.sheet_names:
        df = xls.parse(aba)
        df["Origem"] = aba
        df["numero_rc"] = df["RC"].astype(str)
        df["numero_sc"] = df["Solicitacao Senior"].astype(str)
        df["data"] = pd.to_datetime(df["Data Cadastro"], errors="coerce")
        df["empresa"] = df["Empresa"]
        df["filial"] = df["Filial"]
        df["link"] = df.get("Link", "")
        dados.append(df[["numero_rc", "numero_sc", "data", "empresa", "filial", "link", "Origem"]])
    return pd.concat(dados, ignore_index=True)
