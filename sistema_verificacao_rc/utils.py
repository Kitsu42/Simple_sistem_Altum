import pandas as pd
from datetime import datetime

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
