import streamlit as st
from database import SessionLocal
from models import RC
import pandas as pd

def pagina_relatorios():
    st.title("📊 Relatório de RCs")
    db = SessionLocal()
    rcs = db.query(RC).all()
    df = pd.DataFrame([{
        "SC": r.numero_sc,
        "Data": r.data_criacao.strftime("%d/%m/%Y"),
        "Status": r.status,
        "Responsável": r.responsavel,
        "OC": r.numero_oc
    } for r in rcs])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar CSV", csv, "relatorio.csv", "text/csv")
    db.close()
