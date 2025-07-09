# views/finalizado.py
import streamlit as st
from banco import SessionLocal
from models import Requisicao
import pandas as pd

def exibir():
    st.title("✅ RCs Finalizadas")
    db = SessionLocal()
    usuario = st.session_state.get("usuario")
    cargo = st.session_state.get("cargo")

    
    rcs = db.query(Requisicao).filter_by(status="finalizado", responsavel=usuario).all()

    if not rcs:
        st.info("Nenhuma RC finalizada.")
    else:
        for rc in rcs:
            with st.expander(f"SC {rc.solicitacao_senior} | RC {rc.rc} | {rc.empresa} - {rc.filial}"):
                st.write(f"Data de criação: {rc.data}")
                st.write(f"Responsável: {rc.responsavel}")
                st.write(f"Número da OC: {rc.numero_oc}")

                if rc.link:
                    st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)

    db.close()

