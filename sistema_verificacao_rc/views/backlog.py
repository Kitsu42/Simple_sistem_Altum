# views/backlog.py
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
    st.subheader("🔍 Filtros")

    with st.form("filtros_form"):
        empresa_filtro = st.text_input("Empresa", value=st.session_state.get("empresa_filtro", ""))
        filial_filtro = st.text_input("Filial", value=st.session_state.get("filial_filtro", ""))
        
        acao_filtro = st.radio("Ação", ["Aplicar", "Limpar"], horizontal=True)
        aplicar = st.form_submit_button("Confirmar")

    if aplicar:
        if acao_filtro == "Aplicar":
            st.session_state["empresa_filtro"] = empresa_filtro
            st.session_state["filial_filtro"] = filial_filtro
        elif acao_filtro == "Limpar":
            st.session_state["empresa_filtro"] = ""
            st.session_state["filial_filtro"] = ""
        st.experimental_rerun()

    if st.session_state.get("cargo") == "admin":
        arquivo = st.file_uploader("Enviar planilha de backlog", type="xlsx")
        if arquivo:
            df = carregar_backlog(arquivo)

            if 'DATA SC' in df.columns:
                df['Dias em aberto'] = pd.to_datetime("today") - pd.to_datetime(df['DATA SC'], errors='coerce')
                df['Dias em aberto'] = df['Dias em aberto'].dt.days

            agrupado = df.groupby(['Nº SC', 'Empresa', 'Filial']).agg({
                'DATA SC': 'first',
                'Dias em aberto': 'min',
                'DESCRICAO': 'count',
                'OBSERVAÇÃO': 'first'
            }).reset_index()

            for i, row in agrupado.iterrows():
                existente = db.query(Requisicao).filter_by(
                    numero_sc=str(row['Nº SC']), empresa=row['Empresa'], filial=row['Filial']
                ).first()

                if not existente:
                    rc = Requisicao(
                        numero_sc=str(row['Nº SC']),
                        data=row['DATA SC'],
                        empresa=row['Empresa'],
                        filial=row['Filial'],
                        status="backlog",
                        link=row.get("OBSERVAÇÃO", "")
                    )
                    db.add(rc)
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
        with st.expander(f"SC {rc.numero_sc} | {rc.empresa} - {rc.filial}"):
            st.write(f"Data de criação: {rc.data}")
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
