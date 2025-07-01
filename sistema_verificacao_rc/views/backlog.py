# views/backlog.py
import streamlit as st
from planilhas import carregar_backlog
import pandas as pd
from banco import SessionLocal
from models import Requisicao

def exibir():
    st.title("Backlog de SCs")
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
            with st.expander(f"SC {row['Nº SC']} | {row['Empresa']} - {row['Filial']}"):
                st.write(f"Quantidade de Itens: {row['DESCRICAO']}")
                st.write(f"Data de criação: {row['DATA SC']}")
                st.write(f"Dias em aberto: {row['Dias em aberto']}")

                if st.button("Iniciar Cotação", key=f"cotacao_{row['Nº SC']}_{i}"):
                    db = SessionLocal()
                    existe = db.query(Requisicao).filter_by(numero_sc=str(row['Nº SC'])).first()
                    if not existe:
                        rc = Requisicao(
                            numero_sc=str(row['Nº SC']),
                            data=row['DATA SC'],
                            empresa=row['Empresa'],
                            filial=row['Filial'],
                            status="em cotação",
                            responsavel=st.session_state.get("usuario", "")
                        )
                        db.add(rc)
                        db.commit()
                        st.success("Cotação iniciada e RC registrada no banco.")
                    else:
                        st.warning("Esta SC já está registrada no sistema.")
                    db.close()