import streamlit as st
from banco import SessionLocal
from models import Requisicao
from utils import STATUS_FINALIZADO


def exibir():
    st.title(\"✅ RCs Finalizadas\")
    db = SessionLocal()
    usuario = st.session_state.get(\"usuario\")
    cargo = st.session_state.get(\"cargo\")

    # Por enquanto admin vê tudo; demais também (ajuste futuro)
    rcs = db.query(Requisicao).filter_by(status=STATUS_FINALIZADO).all()

    if not rcs:
        st.info(\"Nenhuma RC finalizada.\")
    else:
        for rc in rcs:
            empresa_nome = rc.empresa_display
            filial_nome = rc.filial_display
            with st.expander(f\"RC {rc.rc} | SC {rc.solicitacao_senior} | {empresa_nome} - {filial_nome}\"):
                st.write(f\"Data de criação: {rc.data}\")
                st.write(f\"Responsável: {rc.responsavel}\")
                st.write(f\"Número da OC: {rc.numero_oc}\")
                if rc.link:
                    st.markdown(f\"[📄 Documento da SC]({rc.link})\", unsafe_allow_html=True)

    db.close()