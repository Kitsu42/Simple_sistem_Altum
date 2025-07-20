import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

# ---- Status padronizados ----
# Mantemos 'backlog' por enquanto; futuramente você renomeia para 'pendente'.
STATUS_BACKLOG = "backlog"
STATUS_EM_COTACAO = "em cotação"
STATUS_FINALIZADO = "finalizado"
STATUS_AGUARD_APROVACAO = "aguardando aprovação"  # futuro
STATUS_ERRO = "erro"


def dias_em_aberto(data_val):
    """Retorna número de dias entre hoje e data_val.
    Aceita date, datetime, string ou None."""
    if not data_val:
        return None
    try:
        data = pd.to_datetime(data_val)
        return (pd.to_datetime("today") - data).days
    except Exception:
        return None

def parse_backlog_xml(file) -> pd.DataFrame:
    """
    Lê um arquivo XML de backlog e retorna um DataFrame com as RCs.
    Espera tags como <RC>, <Solicitacao>, <Empresa>, <Filial>, <Data>, <Link>.
    """
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        rows = []
        for rc in root.findall(".//RC"):
            rows.append({
                "rc": rc.findtext("Numero", default=""),
                "solicitacao_senior": rc.findtext("Solicitacao", default=""),
                "empresa": rc.findtext("Empresa", default=""),
                "filial": rc.findtext("Filial", default=""),
                "data": pd.to_datetime(rc.findtext("Data", default=""), errors="coerce"),
                "link": rc.findtext("Link", default=""),
            })
        return pd.DataFrame(rows)
    except Exception as e:
        raise ValueError(f"Erro ao ler XML: {e}")


def parse_backlog_excel(file) -> pd.DataFrame:
    """
    Lê um arquivo Excel de backlog e retorna um DataFrame com colunas padronizadas.
    """
    try:
        df = pd.read_excel(file)
        df.columns = [c.strip().lower() for c in df.columns]
        mapeamento = {
            "rc": "rc",
            "sc": "solicitacao_senior",
            "empresa": "empresa",
            "filial": "filial",
            "data": "data",
            "link": "link",
        }
        df = df.rename(columns={c: mapeamento.get(c, c) for c in df.columns})
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
        return df
    except Exception as e:
        raise ValueError(f"Erro ao ler Excel: {e}")

