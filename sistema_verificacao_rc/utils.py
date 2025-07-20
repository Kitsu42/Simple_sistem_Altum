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

    Colunas esperadas na origem:
      RC
      Solicitacao Senior
      Data Cadastro
      Data Prevista
      Filial  -> "1 - 03.277.956/0001-23 - Goiania"
      Observacoes
      Usuario
      Link

    DataFrame de saída: colunas em minúsculo + campos derivados:
      rc, solicitacao_senior, data_cadastro, data_prevista, filial_raw,
      filial_cod, filial_cnpj, filial_nome, observacoes, usuario, link
    """
    df = pd.read_excel(arquivo_excel, dtype=str)

    # Normaliza nomes de coluna (insensível a espaços/maiúsculas)
    norm_map = {c.lower().strip(): c for c in df.columns}

    def get_col(name):
        return norm_map.get(name.lower())

    # Extrai apenas as colunas relevantes se existirem
    cols_keep = []
    for logical, raw in [
        ("rc", get_col("rc")),
        ("Solicitacao Senior", get_col("solicitacao senior")),
        ("Data Cadastro", get_col("data cadastro")),
        ("Data Prevista", get_col("data prevista")),
        ("Filial", get_col("filial")),
        ("Observacoes", get_col("observacoes")),
        ("Usuario", get_col("usuario")),
        ("Link", get_col("link")),
    ]:
        if raw:
            cols_keep.append(raw)
    df = df[cols_keep].copy()

    # Strip strings
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Datas
    if get_col("data cadastro"):
        df["Data Cadastro"] = pd.to_datetime(df[get_col("data cadastro")], errors="coerce")
    if get_col("data prevista"):
        df["Data Prevista"] = pd.to_datetime(df[get_col("data prevista")], errors="coerce")

    # Quebra da coluna Filial
    filial_col = get_col("filial")
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

    # Renomeia p/ padrão
    rename_map = {}
    if get_col("rc"): rename_map[get_col("rc")] = "rc"
    if get_col("solicitacao senior"): rename_map[get_col("solicitacao senior")] = "solicitacao_senior"
    if get_col("data cadastro"): rename_map[get_col("data cadastro")] = "data_cadastro"
    if get_col("data prevista"): rename_map[get_col("data prevista")] = "data_prevista"
    if get_col("filial"): rename_map[get_col("filial")] = "filial_raw"
    if get_col("observacoes"): rename_map[get_col("observacoes")] = "observacoes"
    if get_col("usuario"): rename_map[get_col("usuario")] = "usuario"
    if get_col("link"): rename_map[get_col("link")] = "link"

    df = df.rename(columns=rename_map)

    return df


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
