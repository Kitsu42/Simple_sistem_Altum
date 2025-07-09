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

    if cargo == "admin":
        rcs = db.query(Requisicao).filter_by(status="finalizado").all()
    else:
        rcs = db.query(Requisicao).filter_by(status="finalizado").all()

    if not rcs:
        st.info("Nenhuma RC finalizada.")
    else:
        for rc in rcs:
            with st.expander(f"RC {rc.rc}  SC {rc.solicitacao_senior} 
             {rc.empresa} - {rc.filial}"):
                st.write(f"Data de criação: {rc.data}")
                st.write(f"Responsável: {rc.responsavel}")
                st.write(f"Número da OC: {rc.numero_oc}")

                if rc.link:
                    st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)

    db.close()

