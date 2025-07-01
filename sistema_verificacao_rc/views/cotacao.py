# views/cotacao.py
import streamlit as st
from banco import SessionLocal
from models import Requisicao

def exibir():
    st.title("Requisições em Cotação")
    db = SessionLocal()
    usuario = st.session_state.get("usuario")

    rcs = db.query(Requisicao).filter_by(status="em cotação", responsavel=usuario).all()

    if not rcs:
        st.info("Nenhuma RC em cotação atribuída a você.")
    else:
        for rc in rcs:
            with st.expander(f"SC {rc.numero_sc} | {rc.empresa} - {rc.filial}"):
                fornecedor = st.text_input("Fornecedor", key=f"fornecedor_{rc.id}")
                nf = st.text_input("Nota Fiscal Recebida?", key=f"nf_{rc.id}")
                cobranca = st.text_input("Cobranca ao fornecedor feita?", key=f"cob_{rc.id}")
                envio = st.text_input("OC enviada ao fornecedor?", key=f"envio_{rc.id}")
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
