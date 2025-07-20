import streamlit as st
import pandas as pd
from sqlalchemy.orm import joinedload
from banco import SessionLocal
from models import Requisicao, Empresa, Filial
from utils import STATUS_BACKLOG, STATUS_EM_COTACAO, dias_em_aberto


def exibir():
    st.title(\"Backlog de SCs\")
    db = SessionLocal()

    # --- Filtros ---
    empresas_db = db.query(Empresa).order_by(Empresa.nome).all()
    empresa_opcoes = [\"Todas\"] + [e.nome for e in empresas_db]
    empresa_sel = st.sidebar.selectbox(\"Empresa\", empresa_opcoes, index=0)

    # Carrega filiais conforme empresa selecionada
    filiais_opcoes = [\"Todas\"]
    if empresa_sel != \"Todas\":
        emp_obj = next((e for e in empresas_db if e.nome == empresa_sel), None)
        if emp_obj:
            filiais_opcoes += [f.nome_exibicao for f in emp_obj.filiais]
    filial_sel = st.sidebar.selectbox(\"Filial\", filiais_opcoes, index=0)

    # Query base backlog
    q = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .filter(Requisicao.status == STATUS_BACKLOG)
    )

    # Filtros aplicados
    if empresa_sel != \"Todas\":
        q = q.join(Requisicao.filial_obj).join(Filial.empresa).filter(Empresa.nome == empresa_sel)
    if filial_sel != \"Todas\":
        q = q.join(Requisicao.filial_obj).filter(Filial.nome_exibicao == filial_sel)

    rcs = q.all()

    if not rcs:
        st.info(\"Nenhuma RC no backlog.\")
        db.close()
        return

    for rc in rcs:
        dias = dias_em_aberto(rc.data)
        empresa_nome = rc.empresa_display
        filial_nome = rc.filial_display

        with st.expander(f\"RC {rc.rc} | SC {rc.solicitacao_senior} | {empresa_nome} - {filial_nome}\"):
            st.write(f\"Data de criação: {rc.data}\")
            if dias is not None:
                if dias >= 10:
                    st.error(f\"⏰ Atenção: {dias} dias em aberto\")
                elif dias >= 5:
                    st.warning(f\"⏳ Em aberto há {dias} dias\")
                else:
                    st.info(f\"📅 Em aberto há {dias} dias\")

            if rc.link:
                st.markdown(f\"[📄 Documento da SC]({rc.link})\", unsafe_allow_html=True)

            if st.button(\"Iniciar Cotação\", key=f\"cotar_{rc.id}\"):
                rc.status = STATUS_EM_COTACAO
                rc.responsavel = st.session_state.get(\"usuario\", \"\")
                db.commit()
                st.success(\"RC movida para cotação\")
                st.experimental_rerun()

    db.close()