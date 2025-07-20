# views/cotacao.py
import streamlit as st
from datetime import date
import pandas as pd  # ainda usamos p/ exibir link etc., mas cálculo de dias vai em date
from banco import SessionLocal
from models import Requisicao
from utils import STATUS_EM_COTACAO, STATUS_FINALIZADO, dias_em_aberto as dias_util


def _calc_dias(data_val):
    """
    Calcula dias abertos de forma segura.
    Tenta primeiro com utilitário (que aceita vários formatos).
    Se falhar, tenta com date.today() - data_val (caso seja date).
    """
    d = dias_util(data_val)
    if d is not None:
        return d
    if isinstance(data_val, date):
        return (date.today() - data_val).days
    try:
        dt = pd.to_datetime(data_val, errors="coerce")
        if pd.isna(dt):
            return None
        return (pd.Timestamp.today().normalize() - dt.normalize()).days
    except Exception:
        return None


def _render_dias_badge(dias):
    """Mostra badge visual conforme dias."""
    if dias is None:
        st.info("📅 Data não informada.")
        return
    if dias >= 10:
        st.error(f"⏰ Atenção: {dias} dias em aberto.")
    elif dias >= 5:
        st.warning(f"⏳ Em aberto há {dias} dias.")
    else:
        st.info(f"📅 Em aberto há {dias} dias.")


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
        dias_open = _calc_dias(rc.data)
        empresa_nome = rc.empresa_display
        filial_nome = rc.filial_display

        with st.expander(f"RC {rc.rc} | SC {rc.solicitacao_senior} | {empresa_nome} - {filial_nome}"):
            st.write(f"Data de criação: {rc.data}")
            _render_dias_badge(dias_open)

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
                    st.rerun()
                    return

    db.close()
