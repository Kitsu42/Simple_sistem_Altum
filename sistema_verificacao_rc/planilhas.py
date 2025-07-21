# planilhas.py
"""
Importador de planilha de backlog de RCs.

Formato Excel esperado (colunas podem variar em capitalização/acentos):
    RC
    Solicitacao Senior (ou Solicitacao / SC)
    Data Cadastro
    Data Prevista     (não armazenada no modelo atual; usamos só para cálculo)
    Filial            (texto com CNPJ/cidade; mapeado para empresa/filial texto)
    Observacoes       (não armazenada no modelo atual)
    Usuario           (solicitante; não armazenado no modelo atual)
    Link              (URL do painel)

ATENÇÃO: O model Requisicao atual NÃO possui campos para Observações, Data Prevista,
Solicitante. Enquanto o schema não for migrado, esses dados não serão persistidos
no banco — apenas exibidos na pré-visualização de importação.
"""

import pandas as pd
import re
from typing import Optional
from sqlalchemy.orm import Session
from models import Requisicao  # usando modelo atual (sem campos extras)

# ------------------------------------------------------------------
# Regex para capturar CNPJ na coluna Filial
# ------------------------------------------------------------------
_CNPJ_RE = re.compile(r"(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})")


def _clean_cnpj(txt: str) -> str:
    if not txt:
        return ""
    m = _CNPJ_RE.search(str(txt))
    if not m:
        return ""
    return "".join(ch for ch in m.group(1) if ch.isdigit())


def _extract_cidade_from_filial(txt: str) -> str:
    """
    Filial vem como '1 - 03.277.956/0001-23 - Goiania'.
    Retorna o último segmento (cidade).
    """
    if not txt:
        return ""
    parts = [p.strip() for p in str(txt).split("-") if p.strip()]
    return parts[-1] if parts else ""


# ------------------------------------------------------------------
# Normalização leve de cabeçalhos (sem necessidade de _normalize_colname)
# ------------------------------------------------------------------
_COLMAP = {
    "rc": "RC",
    "requisicao": "RC",
    "requisicao compra": "RC",

    "solicitacao senior": "SC",
    "solicitacao": "SC",
    "sc": "SC",

    "data cadastro": "Data Cadastro",
    "dt cadastro": "Data Cadastro",
    "cadastro": "Data Cadastro",

    "data prevista": "Data Prevista",
    "dt prevista": "Data Prevista",

    "filial": "Filial",

    "observacoes": "Observacoes",
    "observacao": "Observacoes",
    "obs": "Observacoes",

    "usuario": "Usuario",
    "solicitante": "Usuario",

    "link": "Link",
    "url": "Link",
}


def _normalize_header_list(cols) -> dict:
    """
    Recebe lista de colunas originais e retorna dict:
        { nome_original: nome_canonico_ou_mesmo }
    """
    ren = {}
    for c in cols:
        norm = str(c).strip().lower()
        mapped = _COLMAP.get(norm, None)
        if mapped:
            ren[c] = mapped
    return ren


# ------------------------------------------------------------------
# Parser Excel
# ------------------------------------------------------------------
def parse_backlog_excel(file) -> pd.DataFrame:
    xls = pd.ExcelFile(file)
    frames = []

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        ren = _normalize_header_list(df.columns)
        df = df.rename(columns=ren)
        df = df.loc[:, ~df.columns.duplicated()]  # <<< Remove duplicatas

        for col in ["RC","SC","Usuario","Data Cadastro","Data Prevista","Filial","Observacoes","Link"]:
            if col not in df.columns:
                df[col] = ""

        df["Origem"] = sheet
        df = df[["RC","SC","Usuario","Data Cadastro","Data Prevista","Filial","Observacoes","Link","Origem"]]
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)
    def _to_date(val):
        try:
            return pd.to_datetime(val, errors="coerce", dayfirst=True).date()
        except Exception:
            return None

    def _parse_date_br(value):
        """
        Converte datas para datetime.date com suporte ao formato DD/MM/YYYY.
        Funciona para strings, pandas.Timestamp ou números serializados do Excel.
        """
        if pd.isna(value):
            return None
        if isinstance(value, (pd.Timestamp, datetime.date)):
            return value.date() if hasattr(value, "date") else value
        try:
            return pd.to_datetime(str(value), dayfirst=True, errors="coerce").date()
        except Exception:
            return None

    out["Data Prevista"] = pd.to_datetime(out["Data Prevista"], errors="coerce", dayfirst=True).dt.date
    out["cnpj"] = out["Filial"].apply(_clean_cnpj)
    out["cidade"] = out["Filial"].apply(_extract_cidade_from_filial)
    return out


# ------------------------------------------------------------------
# Importação para o banco (modelo atual)
# ------------------------------------------------------------------
def importar_backlog(df: pd.DataFrame, session: Session) -> int:
    """
    Importa RCs para o banco usando o modelo Requisicao (schema novo / compatível).
    Campos persistidos:
      rc, solicitacao_senior, data, data_prevista, solicitante, observacoes,
      empresa_txt, filial_txt, status, link.
    """
    import datetime

    def _clean_str(val):
        if val is None:
            return None
        s = str(val).strip()
        if s == "" or s.lower() in ("nan","none","null"):
            return None
        return s

    novos = 0
    for _, row in df.iterrows():
        rc_num = _clean_str(row.get("RC"))
        sc_num = _clean_str(row.get("SC"))

        # Ignora linha vazia
        if not rc_num and not sc_num:
            continue

        # datas
        data_cad = row.get("Data Cadastro")
        data_prev = row.get("Data Prevista")

        # fallback: usa Prevista se Cadastro vazio
        if (data_cad is None or pd.isna(data_cad)) and (data_prev is not None and not pd.isna(data_prev)):
            data_cad = data_prev

        # fallback final: hoje
        if data_cad is None or pd.isna(data_cad):
            data_cad = datetime.date.today()

        # texto
        filial_txt = _clean_str(row.get("Filial"))
        empresa_txt = None  # pode tentar heurística futura
        obs = _clean_str(row.get("Observacoes"))
        solicitante = _clean_str(row.get("Usuario"))
        link = _clean_str(row.get("Link"))

        # Dedup
        q = session.query(Requisicao)
        if sc_num:
            q = q.filter(Requisicao.solicitacao_senior == sc_num)
        elif rc_num:
            q = q.filter(Requisicao.rc == rc_num)
        existente = q.first()
        if existente:
            continue

        novo = Requisicao(
            rc=rc_num,
            solicitacao_senior=sc_num,
            data=data_cad,
            data_prevista=data_prev,
            solicitante=solicitante,
            observacoes=obs,
            empresa_txt=empresa_txt,
            filial_txt=filial_txt,
            status="backlog",
            link=link,
        )
        session.add(novo)
        novos += 1

    if novos:
        session.commit()
    return novos