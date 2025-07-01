# utils.py
from datetime import datetime

def dias_em_aberto(data_str):
    try:
        data = pd.to_datetime(data_str)
        return (datetime.today() - data).days
    except:
        return None
