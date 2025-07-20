# views/backlog.py
import streamlit as st
import pandas as pd
from sqlalchemy.orm import joinedload
from banco import SessionLocal
from models import Requisicao, Empresa, Filial
from utils import STATUS_BACKLOG, STATUS_EM_COTACAO, dias_em_aberto


def _fmt_date(d):
    """Formata data; aceita date, datetime, string, None."""
    if not d:
        return "—"
    try:
        return pd.to_datetime(d, errors="coerce").strftime("%d/%m/%Y")
    except Exception:
        return str(d)


def _dias_badge(dias):
    """Mostra badge por tempo em aberto."""
    if dias is None:
        st.info("📅 Sem data de cadastro.")
    elif dias >= 10:
        st.error(f"⏰ {dias} dias em aberto.")
    elif dias >= 5:
        st.warning(f"⏳ Em aberto há {dias} dias.")
    else:
        st.info(f"📅 Em aberto há {dias} dias.")


def exibir():
    st.title("Backlog de SCs")
    db = SessionLocal()

    # ----------------------------
    # Filtros (barra lateral)
    # ----------------------------
    empresas_db = db.query(Empresa).order_by(Empresa.nome).all()
    empresa_opcoes = ["Todas"] + [e.nome for e in empresas_db]
    empresa_sel = st.sidebar.selectbox("Empresa", empresa_opcoes, index=0)

    filiais_opcoes = ["Todas"]
    if empresa_sel != "Todas":
        emp_obj = next((e for e in empresas_db if e.nome == empresa_sel), None)
        if emp_obj:
            filiais_opcoes += [f.nome_exibicao for f in emp_obj.filiais]
    filial_sel = st.sidebar.selectbox("Filial", filiais_opcoes, index=0)

    # ----------------------------
    # Query base backlog
    # ----------------------------
    q = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .filter(Requisicao.status == STATUS_BACKLOG)
    )

    if empresa_sel != "Todas":
        q = q.join(Requisicao.filial_obj).join(Filial.empresa).filter(Empresa.nome == empresa_sel)
    if filial_sel != "Todas":
        q = q.join(Requisicao.filial_obj).filter(Filial.nome_exibicao == filial_sel)

    rcs = q.all()

    if not rcs:
        st.info("Nenhuma RC no backlog.")
        db.close()
        return

    # ----------------------------
    # Renderiza cada RC
    # ----------------------------
    for rc in rcs:
        dias = dias_em_aberto(rc.data)
        empresa_nome = rc.empresa_display
        filial_nome = rc.filial_display

        header = f"RC {rc.rc} | SC {rc.solicitacao_senior or '—'} | {empresa_nome} - {filial_nome}"
        with st.expander(header):
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.write(f"**Data Cadastro:** {_fmt_date(rc.data)}")
            with col2:
                st.write(f"**Data Prevista:** {_fmt_date(getattr(rc, 'data_prevista', None))}")
            with col3:
                _dias_badge(dias)

            st.write(f"**Solicitante:** {getattr(rc, 'solicitante', '') or '—'}")

            if getattr(rc, "observacoes", None):
                with st.expander("📝 Observações do solicitante"):
                    st.write(rc.observacoes)
            else:
                st.caption("Sem observações.")

            if rc.link:
                st.markdown(f"[📄 Abrir no painel]({rc.link})", unsafe_allow_html=True)

            if st.button("Iniciar Cotação", key=f"cotar_{rc.id}"):
                rc.status = STATUS_EM_COTACAO
                rc.responsavel = st.session_state.get("usuario", "")
                db.commit()
                st.success("RC movida para cotação.")
                st.rerun()
                return  # encerra após rerun

    db.close()
