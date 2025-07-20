# views/cotacao.py
import streamlit as st
import pandas as pd
from datetime import date
from banco import SessionLocal
from models import Requisicao
from utils import STATUS_EM_COTACAO, STATUS_FINALIZADO, dias_em_aberto


def _fmt_date(d):
    if not d:
        return "—"
    try:
        return pd.to_datetime(d, errors="coerce").strftime("%d/%m/%Y")
    except Exception:
        return str(d)


def _badge_dias(dias):
    if dias is None:
        st.info("📅 Sem data de cadastro.")
    elif dias >= 10:
        st.error(f"⏰ {dias} dias em aberto.")
    elif dias >= 5:
        st.warning(f"⏳ Em aberto há {dias} dias.")
    else:
        st.info(f"📅 Em aberto há {dias} dias.")


def _dias_para_prevista(data_prev):
    if not data_prev:
        return None
    try:
        dprev = pd.to_datetime(data_prev, errors="coerce")
        if pd.isna(dprev):
            return None
        dprev = dprev.date()
    except Exception:
        return None
    return (date.today() - dprev).days * -1  # positivo = falta(m) dias; negativo = atraso


def exibir():
    st.title("Minhas cotações")
    db = SessionLocal()
    usuario = st.session_state.get("usuario")

    rcs = db.query(Requisicao).filter_by(status=STATUS_EM_COTACAO, responsavel=usuario).all()

    if not rcs:
        st.info("Nenhuma RC em cotação atribuída a você.")
        db.close()
        return

    for rc in rcs:
        dias_open = dias_em_aberto(rc.data)
        empresa_nome = rc.empresa_display
        filial_nome = rc.filial_display
        dias_para_prev = _dias_para_prevista(getattr(rc, "data_prevista", None))

        header = f"RC {rc.rc} | SC {rc.solicitacao_senior or '—'} | {empresa_nome} - {filial_nome}"
        with st.expander(header):
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.write(f"**Data Cadastro:** {_fmt_date(rc.data)}")
            with col2:
                st.write(f"**Data Prevista:** {_fmt_date(getattr(rc, 'data_prevista', None))}")
            with col3:
                _badge_dias(dias_open)

            # Indicador de prazo (comparação Data Prevista vs hoje)
            if dias_para_prev is not None:
                if dias_para_prev < 0:
                    st.error(f"📉 Atrasado {abs(dias_para_prev)} dia(s) além da Data Prevista.")
                elif dias_para_prev == 0:
                    st.warning("⚠️ Vence hoje (Data Prevista).")
                else:
                    st.info(f"⏳ Falta(m) {dias_para_prev} dia(s) para Data Prevista.")

            st.write(f"**Solicitante:** {getattr(rc, 'solicitante', '') or '—'}")

            if getattr(rc, "observacoes", None):
                with st.expander("📝 Observações do solicitante"):
                    st.write(rc.observacoes)
            else:
                st.caption("Sem observações.")

            if rc.link:
                st.markdown(f"[📄 Abrir no painel]({rc.link})", unsafe_allow_html=True)

            # Campos operacionais (ainda não persistidos; placeholders)
            fornecedor = st.text_input("Fornecedor", key=f"fornecedor_{rc.id}")
            st.checkbox("Cobrar orçamento", key=f"cob_{rc.id}")
            st.checkbox("OC enviada ao fornecedor", key=f"envio_{rc.id}")
            st.checkbox("NF Recebida", key=f"nf_{rc.id}")
            st.checkbox("NF e Boleto anexados", key=f"anxBNF_{rc.id}")

            numero_oc = st.text_input("Númer
