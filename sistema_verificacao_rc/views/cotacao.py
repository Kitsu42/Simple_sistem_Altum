# views/cotacao.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Requisicao
from utils import STATUS_EM_COTACAO, STATUS_FINALIZADO


def exibir():
    st.title("Minhas cotações")
    db = SessionLocal()
    usuario = st.session_state.get("usuario")

    rcs = db.query(Requisicao).filter_by(status=STATUS_EM_COTACAO, responsavel=usuario).all()

    if not rcs:
        st.info("Nenhuma RC em cotação atribuída a você.")
    else:
        for rc in rcs:
            dias_open = (pd.to_datetime("today") - pd.to_datetime(rc.data)).days
            empresa_nome = rc.empresa_display
            filial_nome = rc.filial_display
            with st.expander(f"RC {rc.rc} | SC {rc.solicitacao_senior} | {empresa_nome} - {filial_nome}"):
                st.write(f"Data de criação: {rc.data}  |  ⏱️ Dias em aberto: {dias_open}")

                if rc.link:
                    st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)

                fornecedor = st.text_input("Fornecedor", key=f"fornecedor_{rc.id}")
                st.checkbox("Cobrar orçamento", key=f"cob_{rc.id}")
                st.checkbox("OC enviada ao fornecedor", key=f"envio_{rc.id}")
                st.checkbox("NF Recebida", key=f"nf_{rc.id}")
                st.checkbox("NF e Boleto anexados", key=f"anxBNF_{rc.id}")

                numero_oc = st.text_input("Número da OC", key=f"oc_{rc.id}")

                if st.button("Finalizar RC", key=f"finaliza_{rc.id}"):
                    if not numero_oc.strip():
                        st.error("Você deve preencher o número da OC antes de finalizar a RC.")
                    else:
                        rc.status = STATUS_FINALIZADO
                        rc.numero_oc = numero_oc
                        db.commit()
                        st.success("RC finalizada com sucesso.")
                        st.experimental_rerun()

    db.close()
