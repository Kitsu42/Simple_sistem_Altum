#backlog.py
import streamlit as st
from planilhas import carregar_backlog
import pandas as pd
from banco import SessionLocal
from models import Requisicao
from sqlalchemy.orm.exc import NoResultFound

def exibir():
    st.title("Backlog de SCs")
    db = SessionLocal()

    # Filtros por empresa e filial (por usuário)
    with st.expander("🔍 Filtros", expanded=False):
        with st.form("filtros_form"):
            empresa_filtro = st.text_input("Empresa", value=st.session_state.get("empresa_filtro", ""))
            filial_filtro = st.text_input("Filial", value=st.session_state.get("filial_filtro", ""))

            acao_filtro = st.radio("Ação", ["Aplicar", "Limpar"], horizontal=True)
            aplicar = st.form_submit_button("Confirmar")

        if aplicar:
            if acao_filtro == "Aplicar":
                st.session_state["empresa_filtro"] = empresa_filtro
                st.session_state["filial_filtro"] = filial_filtro
            else:
                st.session_state["empresa_filtro"] = ""
                st.session_state["filial_filtro"] = ""
            st.experimental_rerun()

    if st.session_state.get("cargo") == "admin":
        arquivo = st.file_uploader("Enviar planilha de backlog", type="xlsx")
        if arquivo:
            df = carregar_backlog(arquivo)

            if 'Data Cadastro' in df.columns:
                df['Dias em aberto'] = pd.to_datetime("today") - pd.to_datetime(df['Data Cadastro'], errors='coerce')
                df['Dias em aberto'] = df['Dias em aberto'].dt.days

            agrupado = df.groupby(['RC', 'Solicitacao Senior', 'Empresa', 'Filial']).agg({
                'Data Cadastro': 'first',
                'Dias em aberto': 'min',
                'Link': 'first'
            }).reset_index()

            for i, row in agrupado.iterrows():
                existente = db.query(Requisicao).filter_by(
                    solicitacao_senior=str(row['Solicitacao Senior']),
                    empresa=row['Empresa'],
                    filial=row['Filial']
                ).first()

                if not existente:
                    rc_obj = Requisicao(
                        rc=str(row['RC']),
                        solicitacao_senior=str(row['Solicitacao Senior']),
                        data=row['Data Cadastro'],
                        empresa=row['Empresa'],
                        filial=row['Filial'],
                        status="backlog",
                        link=row.get("Link", "")
                    )
                    db.add(rc_obj)
            db.commit()
            st.success("Planilha importada com sucesso.")

    query = db.query(Requisicao).filter_by(status="backlog")

    # Aplica os filtros do usuário se estiverem definidos
    if st.session_state.get("empresa_filtro"):
        query = query.filter(Requisicao.empresa.ilike(f"%{st.session_state['empresa_filtro']}%"))
    if st.session_state.get("filial_filtro"):
        query = query.filter(Requisicao.filial.ilike(f"%{st.session_state['filial_filtro']}%"))

    rcs = query.all()

    for i, rc in enumerate(rcs):
        dias_em_aberto = (pd.to_datetime("today") - pd.to_datetime(rc.data)).days

        with st.expander(f"SC {rc.solicitacao_senior} | RC {rc.rc} | {rc.empresa} - {rc.filial}"):
            st.write(f"Data de criação: {rc.data}")

            if dias_em_aberto >= 10:
                st.error(f"⏰ Atenção: {dias_em_aberto} dias em aberto")
            elif dias_em_aberto >= 5:
                st.warning(f"⏳ Em aberto há {dias_em_aberto} dias")
            else:
                st.info(f"📅 Em aberto há {dias_em_aberto} dias")

            if rc.link:
                st.markdown(f"[📄 Documento da SC]({rc.link})", unsafe_allow_html=True)
            if st.button("Iniciar Cotação", key=f"cotar_{rc.id}"):
                rc.status = "em cotação"
                rc.responsavel = st.session_state.get("usuario", "")
                db.commit()
                st.success("RC movida para cotação")

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
