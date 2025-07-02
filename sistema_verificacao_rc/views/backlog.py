import streamlit as st
from planilhas import carregar_backlog
import pandas as pd
from banco import SessionLocal
from models import Requisicao
from sqlalchemy.orm.exc import NoResultFound

def exibir():
    st.title("Backlog de SCs")
    db = SessionLocal()

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
                'DESCRICAO': 'count'
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
                        status="backlog"
                    )
                    db.add(rc)
            db.commit()
            st.success("Planilha importada com sucesso.")

    rcs = db.query(Requisicao).filter_by(status="backlog").all()

    for i, rc in enumerate(rcs):
        with st.expander(f"SC {rc.numero_sc} | {rc.empresa} - {rc.filial}"):
            st.write(f"Data de criação: {rc.data}")
            if st.button("Iniciar Cotação", key=f"cotar_{rc.id}"):
                rc.status = "em cotação"
                rc.responsavel = st.session_state.get("usuario", "")
                db.commit()
                st.success("RC movida para cotação")

    db.close()
