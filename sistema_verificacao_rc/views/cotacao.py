# views/cotacao.py
import streamlit as st
from banco import SessionLocal
from models import Requisicao
import pandas as pd

def exibir():
    st.title("Minhas cotações")
    db = SessionLocal()
    usuario = st.session_state.get("usuario")

    rcs = db.query(Requisicao).filter_by(status="em cotação", responsavel=usuario).all()

    if not rcs:
        st.info("Nenhuma RC em cotação atribuída a você.")
    else:
        for rc in rcs:
            with st.expander(f"RC {rc.rc} | SC {rc.solicitacao_senior} | {rc.empresa} - {rc.filial}"):
                dias_em_aberto = (pd.to_datetime("today") - pd.to_datetime(rc.data)).days
                st.write(f"Data de criação: {rc.data}  |  ⏱️ Dias em aberto: {dias_em_aberto}")

                if rc.link:
                    st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)

                fornecedor = st.text_input("Fornecedor", key=f"fornecedor_{rc.id}")

                nf_ok = st.checkbox("NF Recebida", key=f"nf_{rc.id}")
                cobrado = st.checkbox("Cobrar orçamento", key=f"cob_{rc.id}")
                cobrarNF = st.checkbox("Cobrar NF", key=f"cobnf_{rc.id}")
                envio_ok = st.checkbox("OC enviada ao fornecedor", key=f"envio_{rc.id}")

                numero_oc = st.text_input("Número da OC", key=f"oc_{rc.id}")

                if st.button("Finalizar RC", key=f"finaliza_{rc.id}"):
                    if not numero_oc.strip():
                        st.error("Você deve preencher o número da OC antes de finalizar a RC.")
                    else:
                        rc.status = "finalizado"
                        rc.numero_oc = numero_oc
                        db.commit()
                        st.success("RC finalizada com sucesso.")

    db.close()
