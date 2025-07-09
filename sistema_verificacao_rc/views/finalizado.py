# views/finalizado.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Requisicao
from datetime import datetime, timedelta

def exibir():
    st.title("✅ RCs Finalizadas")
    db = SessionLocal()

    # Filtro de datas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", datetime.today() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data final", datetime.today())

    query = db.query(Requisicao).filter(
        Requisicao.status == "finalizado",
        Requisicao.data >= data_inicio,
        Requisicao.data <= data_fim
    )

    rcs = query.all()

    if not rcs:
        st.info("Nenhuma RC finalizada no período.")
    else:
        for rc in rcs:
            with st.expander(f"RC {rc.rc} | SC {rc.solicitacao_senior} | {rc.empresa} - {rc.filial}"):
                st.write(f"Data: {rc.data}")
                st.write(f"Responsável: {rc.responsavel}")
                st.write(f"Número da OC: {rc.numero_oc}")
                if rc.link:
                    st.markdown(f"[📄 Documento]({rc.link})", unsafe_allow_html=True)

    db.close()
