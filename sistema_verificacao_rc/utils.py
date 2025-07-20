# utils.py
import pandas as pd
import re
import xml.etree.ElementTree as ET
from datetime import datetime

# ---- Status padronizados ----
STATUS_BACKLOG = "backlog"              # futuramente: "pendente"
STATUS_EM_COTACAO = "em cotação"
STATUS_FINALIZADO = "finalizado"
STATUS_AGUARD_APROVACAO = "aguardando aprovação"  # reservado
STATUS_ERRO = "erro"


# Dias em aberto
def dias_em_aberto(data_val):
    """Retorna número de dias entre hoje e data_val.
    Aceita date, datetime, string ou None. Retorna None se inválido."""
    if not data_val:
        return None
    try:
        data = pd.to_datetime(data_val, errors="coerce")
        if pd.isna(data):
            return None
        return (pd.Timestamp.today().normalize() - data.normalize()).days
    except Exception:
        return None


# Limpeza genérica de CNPJ
def limpa_cnpj(texto: str) -> str:
    if not texto:
        return ""
    return re.sub(r"\D+", "", str(texto))

def parse_backlog_excel(arquivo_excel) -> pd.DataFrame:
    """
    Lê a planilha de backlog (formato RC real) e retorna DataFrame padronizado.

    Saída: rc, solicitacao_senior, data_cadastro, data_prevista,
           filial_raw, filial_cod, filial_cnpj, filial_nome,
           observacoes, solicitante, link
    """
    df = pd.read_excel(arquivo_excel, dtype=str)

    # Normaliza nomes
    norm_map = {c.lower().strip(): c for c in df.columns}
    def gc(name): return norm_map.get(name.lower())

    cols_keep = [c for c in [
        gc("rc"),
        gc("solicitacao senior"),
        gc("data cadastro"),
        gc("data prevista"),
        gc("filial"),
        gc("observacoes"),
        gc("usuario"),
        gc("link"),
    ] if c]
    df = df[cols_keep].copy()

    # strip
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # datas
    if gc("data cadastro"):
        df["Data Cadastro"] = pd.to_datetime(df[gc("data cadastro")], errors="coerce")
    else:
        df["Data Cadastro"] = pd.NaT

    if gc("data prevista"):
        df["Data Prevista"] = pd.to_datetime(df[gc("data prevista")], errors="coerce")
    else:
        df["Data Prevista"] = pd.NaT

    # filial split
    filial_col = gc("filial")
    if filial_col:
        def split_filial(txt):
            if pd.isna(txt):
                return pd.Series([None, None, None])
            partes = [p.strip() for p in str(txt).split(" - ")]
            cod = partes[0] if len(partes) > 0 else None
            cnpj = limpa_cnpj(partes[1]) if len(partes) > 1 else None
            nome = partes[2] if len(partes) > 2 else None
            return pd.Series([cod, cnpj, nome])
        df[["Filial_Cod", "Filial_CNPJ", "Filial_Nome"]] = df[filial_col].apply(split_filial)
    else:
        df["Filial_Cod"] = None
        df["Filial_CNPJ"] = None
        df["Filial_Nome"] = None

    # renomeia
    rename_map = {}
    if gc("rc"): rename_map[gc("rc")] = "rc"
    if gc("solicitacao senior"): rename_map[gc("solicitacao senior")] = "solicitacao_senior"
    if gc("filial"): rename_map[gc("filial")] = "filial_raw"
    if gc("observacoes"): rename_map[gc("observacoes")] = "observacoes"
    if gc("usuario"): rename_map[gc("usuario")] = "solicitante"  # <--- importante!
    if gc("link"): rename_map[gc("link")] = "link"

    df = df.rename(columns=rename_map)

    # padroniza datas para colunas finais
    df["data_cadastro"] = df["Data Cadastro"]
    df["data_prevista"] = df["Data Prevista"]

    # garante ordem friendly
    out_cols = [
        "rc", "solicitacao_senior",
        "data_cadastro", "data_prevista",
        "filial_raw", "Filial_Cod", "Filial_CNPJ", "Filial_Nome",
        "observacoes", "solicitante", "link"
    ]
    existing = [c for c in out_cols if c in df.columns]
    return df[existing]


# Parse backlog XML
def parse_backlog_xml(file) -> pd.DataFrame:
    """
    Lê um arquivo XML de backlog (layout genérico) e devolve DataFrame.
    Ajuste tags conforme necessário.
    """
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        rows = []
        for node in root.findall(".//RC"):
            rows.append({
                "rc": node.findtext("Numero", default=""),
                "solicitacao_senior": node.findtext("Solicitacao", default=""),
                "data_cadastro": pd.to_datetime(node.findtext("Data", default=""), errors="coerce"),
                "filial_raw": node.findtext("Filial", default=""),
                "link": node.findtext("Link", default=""),
            })
        return pd.DataFrame(rows)
    except Exception as e:
        raise ValueError(f"Erro ao ler XML: {e}")
