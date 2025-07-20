# views/backlog.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Requisicao, Empresa, Filial
from utils import STATUS_BACKLOG, STATUS_EM_COTACAO, dias_em_aberto


def exibir():
    st.title("Backlog de SCs")
    db = SessionLocal()

    # Carregar lista de empresas / filiais cadastradas
    empresas_db = db.query(Empresa).order_by(Empresa.nome).all()
    empresa_opcoes = ["Todas"] + [e.nome for e in empresas_db]
    empresa_sel = st.sidebar.selectbox("Empresa", empresa_opcoes, index=0)

    # Prepara filiais dependendo da empresa
    filiais_opcoes = ["Todas"]
    if empresa_sel != "Todas":
        emp_obj = next((e for e in empresas_db if e.nome == empresa_sel), None)
        if emp_obj:
            filiais_opcoes += [f.nome_exibicao for f in emp_obj.filiais]
    filial_sel = st.sidebar.selectbox("Filial", filiais_opcoes, index=0)

    # Busca RCs em backlog
    rcs = db.query(Requisicao).filter(Requisicao.status == STATUS_BACKLOG).all()

    # Filtro por empresa/filial em memória (usando display para respeitar normalizados e legado)
    def match_empresa(rc):
        if empresa_sel == "Todas":
            return True
        return rc.empresa_display == empresa_sel

    def match_filial(rc):
        if filial_sel == "Todas":
            return True
        return rc.filial_display == filial_sel

    rcs = [rc for rc in rcs if match_empresa(rc) and match_filial(rc)]

    if not rcs:
        st.info("Nenhuma RC no backlog.")
        db.close()
        return

    for rc in rcs:
        dias = dias_em_aberto(rc.data)
        empresa_nome = rc.empresa_display
        filial_nome = rc.filial_display

        with st.expander(f"RC {rc.rc} | SC {rc.solicitacao_senior} | {empresa_nome} - {filial_nome}"):
            st.write(f"Data de criação: {rc.data}")
            if dias is not None:
                if dias >= 10:
                    st.error(f"⏰ Atenção: {dias} dias em aberto")
                elif dias >= 5:
                    st.warning(f"⏳ Em aberto há {dias} dias")
                else:
                    st.info(f"📅 Em aberto há {dias} dias")

            if rc.link:
                st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)

            if st.button("Iniciar Cotação", key=f"cotar_{rc.id}"):
                rc.status = STATUS_EM_COTACAO
                rc.responsavel = st.session_state.get("usuario", "")
                db.commit()
                st.success("RC movida para cotação")
                st.experimental_rerun()

    db.close()
