import streamlit as st
from database import SessionLocal
from models import RC

def pagina_cotacao():
    st.title("📋 RCs em Cotação")
    db = SessionLocal()
    rcs = db.query(RC).filter(RC.status == "cotação").all()
    for rc in rcs:
        with st.expander(f"SC {rc.numero_sc}"):
            rc.fornecedor_nome = st.text_input("Fornecedor", rc.fornecedor_nome or "", key=f"f{rc.id}")
            rc.fornecedor_telefone = st.text_input("Telefone", rc.fornecedor_telefone or "", key=f"t{rc.id}")
            rc.fornecedor_empresa = st.text_input("Empresa Forn.", rc.fornecedor_empresa or "", key=f"e{rc.id}")
            rc.lembrete_nf = st.checkbox("Anexar NF", rc.lembrete_nf, key=f"nf{rc.id}")
            rc.lembrete_cobrar = st.checkbox("Cobrar fornecedor", rc.lembrete_cobrar, key=f"c{rc.id}")
            rc.lembrete_oc = st.checkbox("Enviar OC", rc.lembrete_oc, key=f"oc{rc.id}")
            if st.button("Salvar", key=f"save{rc.id}"):
                db.commit()
                st.success("Informações salvas.")
    db.close()
