# planilhas.py
import pandas as pd
import re
from typing import Optional
from sqlalchemy.orm import Session
from models import Requisicao, Filial

# Regex para capturar CNPJ
_CNPJ_RE = re.compile(r"(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})")

def _clean_cnpj(txt: str) -> str:
    if not txt:
        return ""
    m = _CNPJ_RE.search(str(txt))
    if not m:
        return ""
    return "".join(ch for ch in m.group(1) if ch.isdigit())

def _extract_cidade_from_filial(txt: str) -> str:
    """Filial vem como '1 - 03.277.956/0001-23 - Goiania'. Pega último token."""
    if not txt:
        return ""
    parts = [p.strip() for p in str(txt).split("-") if p.strip()]
    return parts[-1] if parts else ""

def parse_backlog_excel(file) -> pd.DataFrame:
    """
    Lê arquivo Excel de backlog (todas as abas) e retorna DF padronizado.
    Espera colunas: RC, Solicitacao Senior, Data Cadastro, Data Prevista, Filial,
                    Observacoes, Usuario, Link (case-insensitive).
    """
    xls = pd.ExcelFile(file)
    frames = []

    colmap = {
        "rc": "RC",
        "solicitacao senior": "SC",
        "solicitacao": "SC",
        "sc": "SC",
        "data cadastro": "Data Cadastro",
        "dt cadastro": "Data Cadastro",
        "data prevista": "Data Prevista",
        "dt prevista": "Data Prevista",
        "filial": "Filial",
        "observacoes": "Observacoes",
        "observacao": "Observacoes",
        "usuario": "Usuario",
        "solicitante": "Usuario",
        "link": "Link",
    }

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        # Normaliza nomes
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )
        norm = {}
        for c in df.columns:
            if c in colmap:
                norm[colmap[c]] = df[c]
        nd = pd.DataFrame(norm)

        # Garante colunas
        for col in ["RC","SC","Data Cadastro","Data Prevista","Filial","Observacoes","Usuario","Link"]:
            if col not in nd.columns:
                nd[col] = ""

        nd["Origem"] = sheet
        frames.append(nd)

    out = pd.concat(frames, ignore_index=True)
    # Datas
    out["Data Cadastro"] = pd.to_datetime(out["Data Cadastro"], errors="coerce", dayfirst=True).dt.date
    out["Data Prevista"]  = pd.to_datetime(out["Data Prevista"], errors="coerce", dayfirst=True).dt.date
    # CNPJ + cidade
    out["cnpj"]   = out["Filial"].apply(_clean_cnpj)
    out["cidade"] = out["Filial"].apply(_extract_cidade_from_filial)
    return out

def _match_filial_row(row: pd.Series, session: Session) -> Optional[Filial]:
    """Tenta localizar Filial no banco por CNPJ ou cidade."""
    cnpj = row.get("cnpj", "")
    cidade = row.get("cidade", "")

    if cnpj:
        f = session.query(Filial).filter(Filial.cnpj == cnpj).first()
        if f:
            return f
    if cidade:
        f = session.query(Filial).filter(Filial.cidade.ilike(f"%{cidade}%")).first()
        if f:
            return f
    return None

def importar_backlog(df: pd.DataFrame, session: Session) -> int:
    """
    Insere novas RCs (status backlog) a partir do DF padronizado.
    Retorna quantidade inserida.
    """
    novos = 0
    for _, row in df.iterrows():
        rc_num = str(row["RC"]).strip() or None
        sc_num = str(row["SC"]).strip() or None
        data_cad = row["Data Cadastro"] if pd.notna(row["Data Cadastro"]) else None
        data_prev = row["Data Prevista"] if pd.notna(row["Data Prevista"]) else None
        obs = str(row["Observacoes"]).strip() or None
        usuario = str(row["Usuario"]).strip() or None
        link = str(row["Link"]).strip() or None
        filial_txt = str(row["Filial"]).strip() or None

        filial_obj = _match_filial_row(row, session)
        filial_id = filial_obj.id if filial_obj else None
        empresa_txt = filial_obj.empresa.nome if filial_obj and filial_obj.empresa else None

        # Dedup
        q = session.query(Requisicao)
        if sc_num:
            q = q.filter(Requisicao.solicitacao_senior == sc_num)
            if filial_id:
                q = q.filter(Requisicao.filial_id == filial_id)
        else:
            if rc_num:
                q = q.filter(Requisicao.rc == rc_num)
        existente = q.first()

        if existente:
            continue

        novo = Requisicao(
            rc=rc_num,
            solicitacao_senior=sc_num,
            data=data_cad,
            data_prevista=data_prev,
            solicitante=usuario,
            observacoes=obs,
            link=link,
            status="backlog",
            filial_id=filial_id,
            empresa_txt=empresa_txt,
            filial_txt=filial_txt,
        )
        session.add(novo)
        novos += 1

    if novos:
        session.commit()
    return novos
