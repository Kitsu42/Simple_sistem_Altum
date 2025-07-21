"""
Importador de planilha de backlog de RCs.

Este módulo lê planilhas Excel provenientes de múltiplas fontes e tenta
normalizar cabeçalhos, extrair dados relevantes e padronizar datas.

Colunas esperadas (capitalização/acentos flexíveis; ver _COLMAP):
    RC
    Solicitacao Senior (ou Solicitacao / SC)
    Data Cadastro   (origem: formato brasileiro DD/MM/AAAA na maioria dos casos)
    Data Prevista   (origem: formato americano MM/DD/AAAA em vários arquivos)
    Filial          (texto com CNPJ/cidade; mapeado para empresa/filial texto)
    Observacoes     (não armazenada no modelo atual)
    Usuario         (solicitante; não armazenado no modelo atual)
    Link            (URL do painel)

ATENÇÃO: O model Requisicao atual NÃO possui campos para Observações, Data Prevista,
Solicitante. Enquanto o schema não for migrado, esses dados não serão persistidos
no banco — apenas exibidos na pré-visualização de importação (vide importar_backlog).

Principais pontos sobre datas:
- "Data Cadastro" costuma vir em padrão BR (dia/mês/ano) -> parse com dayfirst=True.
- "Data Prevista" frequentemente vem em padrão US (mês/dia/ano) -> parse com dayfirst=False.
- Em planilhas misturadas, alguns valores podem estar no formato numérico serial do Excel.
- Todas as conversões retornam objetos datetime.date ou None.

Use as_display_br(df) para gerar *strings* formatadas (DD/MM/AAAA) apenas para exibição.
"""

from __future__ import annotations

import pandas as pd
import re
import datetime as dt
import numpy as np
from typing import Optional, Iterable, Mapping
from sqlalchemy.orm import Session
from models import Requisicao

# ------------------------------------------------------------------
# Excel date system base (Windows 1900 system). Pandas usa 1899-12-30
# para compensar o bug do ano bissexto 1900 do Excel.
# ------------------------------------------------------------------
_EXCEL_ORIGIN = "1899-12-30"

# ------------------------------------------------------------------
# Regex para capturar CNPJ na coluna Filial
# ------------------------------------------------------------------
_CNPJ_RE = re.compile(r"(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})")


def _clean_cnpj(txt: str) -> str:
    """Extrai dígitos de um CNPJ presente em *txt*.

    Retorna string vazia se nenhum CNPJ válido for encontrado.
    """
    if not txt:
        return ""
    m = _CNPJ_RE.search(str(txt))
    if not m:
        return ""
    return "".join(ch for ch in m.group(1) if ch.isdigit())


def _extract_cidade_from_filial(txt: str) -> str:
    """Extrai a cidade do campo *Filial*.

    Ex.: "1 - 03.277.956/0001-23 - Goiania" -> "Goiania".
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


def _normalize_header_list(cols: Iterable) -> Mapping:
    """Mapeia nomes originais de colunas para nomes canônicos.

    Retorna dict {original: canonico}. Colunas não mapeadas são ignoradas
    (mantêm nome original).
    """
    ren = {}
    for c in cols:
        norm = str(c).strip().lower()
        mapped = _COLMAP.get(norm)
        if mapped:
            ren[c] = mapped
    return ren


# ------------------------------------------------------------------
# Parsing de datas
# ------------------------------------------------------------------

def _parse_excel_serial(value) -> Optional[dt.date]:
    """Tenta converter números seriais do Excel em *datetime.date*.

    Retorna *None* em caso de falha.
    """
    try:
        return pd.to_datetime(value, origin=_EXCEL_ORIGIN, unit="D", errors="raise").date()
    except Exception:  # noqa: BLE001 - conversão best-effort
        return None


def _parse_date_known_fmt(value, *, dayfirst: bool = False, fmt: Optional[str] = None) -> Optional[dt.date]:
    """Conversão robusta de qualquer valor para *datetime.date*.

    Ordem de tentativa:
    1. Valores nulos -> None.
    2. Já datetime/date -> date.
    3. Números (ou strings numéricas) -> serial Excel.
    4. Se *fmt* informado -> parse estrito com *format=fmt*.
    5. Parse flexível com *dayfirst* preferido.
    6. Fallback com ordem oposta.
    """
    if pd.isna(value) or value == "":
        return None

    # Já datetime/date
    if isinstance(value, (pd.Timestamp, dt.datetime, dt.date)):
        return value.date() if hasattr(value, "date") else value

    # Número? (inclui strings numéricas)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        d = _parse_excel_serial(value)
        if d is not None:
            return d
    else:
        # tenta converter string numérica para float
        try:
            if str(value).strip().replace(".", "", 1).isdigit():
                d = _parse_excel_serial(float(value))
                if d is not None:
                    return d
        except Exception:  # noqa: BLE001
            pass

    s = str(value).strip()

    # Formato explícito
    if fmt is not None:
        dt1 = pd.to_datetime(s, format=fmt, errors="coerce")
        if not pd.isna(dt1):
            return dt1.date()

    # Ordem preferida
    dt1 = pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
    if not pd.isna(dt1):
        return dt1.date()

    # Fallback: ordem oposta
    dt2 = pd.to_datetime(s, errors="coerce", dayfirst=not dayfirst)
    if not pd.isna(dt2):
        return dt2.date()

    return None


def _parse_date_br(value) -> Optional[dt.date]:
    """Parse específico para formato brasileiro (DD/MM/AAAA)."""
    return _parse_date_known_fmt(value, dayfirst=True, fmt="%d/%m/%Y")


def _parse_date_us(value) -> Optional[dt.date]:
    """Parse específico para formato americano (MM/DD/AAAA)."""
    return _parse_date_known_fmt(value, dayfirst=False, fmt="%m/%d/%Y")


# ------------------------------------------------------------------
# Função utilitária de exibição
# ------------------------------------------------------------------

def as_display_br(df: pd.DataFrame, cols=("Data Cadastro", "Data Prevista")) -> pd.DataFrame:
    """Retorna cópia *df* com colunas de data formatadas como strings BR.

    Valores nulos viram string vazia.
    """
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda d: d.strftime("%d/%m/%Y") if isinstance(d, (dt.date, dt.datetime)) else ("" if pd.isna(d) else str(d))
            )
    return df


# ------------------------------------------------------------------
# Parser principal de backlog Excel
# ------------------------------------------------------------------

def parse_backlog_excel(file) -> pd.DataFrame:
    """Lê um arquivo Excel (caminho ou file-like) e retorna DataFrame normalizado.

    - Normaliza headers conhecidos (_COLMAP).
    - Garante colunas esperadas; cria vazias se faltarem.
    - Adiciona coluna "Origem" com o nome da planilha.
    - Converte datas com regras distintas para Cadastro (BR) e Prevista (US).
    - Extrai CNPJ e cidade de *Filial*.
    """
    xls = pd.ExcelFile(file)
    frames = []

    expected = ["RC","SC","Usuario","Data Cadastro","Data Prevista","Filial","Observacoes","Link"]

    for sheet in xls.sheet_names:
        # dtype=object impede conversões automáticas agressivas; usamos nossos parsers.
        df = xls.parse(sheet, dtype=object)

        ren = _normalize_header_list(df.columns)
        df = df.rename(columns=ren)

        # Remove duplicatas de header mantendo a primeira ocorrência
        df = df.loc[:, ~df.columns.duplicated()]

        # Garante colunas esperadas
        for col in expected:
            if col not in df.columns:
                df[col] = ""

        df["Origem"] = sheet
        df = df[expected + ["Origem"]]
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)

    # Conversões de data coluna a coluna
    out["Data Cadastro"] = out["Data Cadastro"].map(_parse_date_br)
    out["Data Prevista"]  = out["Data Prevista"].map(_parse_date_us)

    # Derivações adicionais
    out["cnpj"] = out["Filial"].apply(_clean_cnpj)
    out["cidade"] = out["Filial"].apply(_extract_cidade_from_filial)

    return out


# ------------------------------------------------------------------
# Importação para o banco (modelo atual)
# ------------------------------------------------------------------

def importar_backlog(df: pd.DataFrame, session: Session) -> int:
    """Importa RCs para o banco usando o modelo Requisicao.

    Campos persistidos:
      rc, solicitacao_senior, data, data_prevista, solicitante, observacoes,
      empresa_txt, filial_txt, status, link.

    Regras:
    - Se Data Cadastro ausente, usa Data Prevista (fallback).
    - Se ambas ausentes, usa data de hoje.
    - Linhas sem RC *e* SC são ignoradas.
    - Dedup por SC; se SC vazio, dedup por RC.
    """
    def _clean_str(val):
        if val is None:
            return None
        s = str(val).strip()
        if s == "" or s.lower() in ("nan", "none", "null"):
            return None
        return s

    hoje = dt.date.today()
    novos = 0

    for _, row in df.iterrows():
        rc_num = _clean_str(row.get("RC"))
        sc_num = _clean_str(row.get("SC"))

        # Ignora linha totalmente vazia
        if not rc_num and not sc_num:
            continue

        # Datas (já devem vir como date/None do parse_backlog_excel, mas reforçamos)
        data_cad = row.get("Data Cadastro")
        if isinstance(data_cad, pd.Timestamp):
            data_cad = data_cad.date()
        data_prev = row.get("Data Prevista")
        if isinstance(data_prev, pd.Timestamp):
            data_prev = data_prev.date()

        # fallback: usa Prevista se Cadastro vazio
        if (data_cad is None or pd.isna(data_cad)) and (data_prev is not None and not pd.isna(data_prev)):
            data_cad = data_prev

        # fallback final: hoje
        if data_cad is None or pd.isna(data_cad):
            data_cad = hoje

        filial_txt = _clean_str(row.get("Filial"))
        empresa_txt = None  # TODO: heurística futura
        obs = _clean_str(row.get("Observacoes"))
        solicitante = _clean_str(row.get("Usuario"))
        link = _clean_str(row.get("Link"))

        # Deduplicação
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
