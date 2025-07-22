# -*- coding: utf-8 -*-
# views/cotacao.py
import streamlit as st
import pandas as pd
from datetime import date
from banco import SessionLocal
from models import Requisicao
from utils import STATUS_EM_COTACAO, STATUS_FINALIZADO, dias_em_aberto


def _fmt_date(d):
    """Formata data para dd/mm/yyyy."""
    if not d:
        return "—"
    try:
        return pd.to_datetime(d, errors="coerce").strftime("%d/%m/%Y")
    except Exception:
        return str(d)


def _badge_dias(dias):
    """Mostra badge colorida com dias em aberto."""
    if dias is None:
        st.info("📅 Sem data de cadastro.")
    elif dias >= 10:
        st.error(f"⏰ {dias} dia(s) em aberto.")
    elif dias >= 5:
        st.warning(f"⏳ Em aberto há {dias} dia(s).")
    else:
        st.info(f"📅 Em aberto há {dias} dia(s).")


def _dias_para_prevista(data_prev):
    """Retorna diferença (em dias) entre hoje e data prevista.
    >0 = falta dias, 0 = hoje, <0 = atraso."""
    if not data_prev:
        return None
    try:
        dprev = pd.to_datetime(data_prev, errors="coerce")
        if pd.isna(dprev):
            return None
        dprev = dprev.date()
    except Exception:
        return None
    return (dprev - date.today()).days


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
            # Datas
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.write(f"**Data Cadastro:** {_fmt_date(rc.data)}")
            with col2:
                st.write(f"**Data Prevista:** {_fmt_date(getattr(rc, 'data_prevista', None))}")
            with col3:
                _badge_dias(dias_open)

            # Indicador de prazo em relação à data prevista
            if dias_para_prev is not None:
                if dias_para_prev < 0:
                    st.error(f"📉 Atrasado {abs(dias_para_prev)} dia(s) além da Data Prevista.")
                elif dias_para_prev == 0:
                    st.warning("⚠️ Vence hoje (Data Prevista).")
                else:
                    st.info(f"⏳ Falta(m) {dias_para_prev} dia(s) para Data Prevista.")

            # Solicitante + Observações
            st.write(f"**Solicitante:** {getattr(rc, 'solicitante', '') or '—'}")

            if getattr(rc, "observacoes", None):
                with st.expander("📝 Observações do solicitante"):
                    st.write(rc.observacoes)
            else:
                st.caption("Sem observações.")

            # Link externo
            if rc.link:
                st.markdown(f"[📄 Abrir no painel]({rc.link})", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Ações da Cotação")

            # Campos operacionais (placeholder – ainda não persistimos)
            fornecedor = st.text_input("Fornecedor", key=f"fornecedor_{rc.id}")
            st.checkbox("Anexar orçamento", key=f"cob_{rc.id}")
            st.checkbox("Enviar OC para o fornecedor", key=f"envio_{rc.id}")
            st.checkbox("NF anexada", key=f"nf_{rc.id}")
            st.checkbox("Boleto anexado", key=f"anxBNF_{rc.id}")
            obsevacao = st.text_area("Notas:", key=f"obs{rc.id}")

            numero_oc = st.text_input("Numero da OC", key=f"oc_{rc.id}")

            if st.button("Finalizar RC", key=f"finaliza_{rc.id}"):
                if not numero_oc.strip():
                    st.error("Você deve preencher o número da OC antes de finalizar a RC.")
                else:
                    rc.status = STATUS_FINALIZADO
                    rc.numero_oc = numero_oc
                    db.commit()
                    st.success("RC finalizada com sucesso.")
                    st.rerun()
                    return

    db.close()
