# views/admin.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Usuario, Requisicao
from sqlalchemy import func
from datetime import datetime, timedelta
from io import BytesIO
import pandas as pd

def exportar_para_excel(dfs: dict) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nome_aba, df in dfs.items():
            # Remover quebras de linha e conversões de tipo
            df_clean = df.applymap(lambda x: str(x).replace("\n", " ").strip() if isinstance(x, str) else x)
            df_clean.to_excel(writer, sheet_name=nome_aba, index=False)
    return output.getvalue()


def exibir():
    if st.session_state.get("reload_admin"):
        st.session_state["reload_admin"] = False
        st.experimental_rerun()

    if st.session_state.get("cargo") != "admin":
        st.error("Acesso restrito.")
        return

    st.title("👥 Administração do Sistema")
    db = SessionLocal()

    st.header("📊 Relatórios de Atividade dos Usuários")
db = SessionLocal()

# Coleta todas as RCs com responsável definido
requisicoes = db.query(Requisicao).filter(Requisicao.responsavel != None).all()

if not requisicoes:
    st.info("Nenhuma RC registrada com responsável definido.")
else:
    df = pd.DataFrame([{
        "responsavel": r.responsavel,
        "status": r.status,
        "data": r.data
    } for r in requisicoes])

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["dias_em_aberto"] = (pd.to_datetime("today") - df["data"]).dt.days

    # 1. RCs em cotação por usuário
    em_cotacao = df[df["status"] == "em cotação"].groupby("responsavel").size().rename("Em Cotação")

    # 2. RCs finalizadas por usuário
    finalizadas = df[df["status"] == "finalizado"].groupby("responsavel").size().rename("Finalizadas")

    # 3. RCs em cotação há mais de 10 dias por usuário
    cotacoes_atrasadas = df[(df["status"] == "em cotação") & (df["dias_em_aberto"] > 10)]
    atrasadas = cotacoes_atrasadas.groupby("responsavel").size().rename("Atrasadas (>10d)")

    # Junta todos em um único dataframe
    resumo = pd.concat([em_cotacao, finalizadas, atrasadas], axis=1).fillna(0).astype(int)
    resumo = resumo.sort_values(by=["Em Cotação", "Finalizadas"], ascending=False)

    st.subheader("📌 Resumo por usuário")
    st.dataframe(resumo)

    # Gráficos (opcional)
    st.subheader("📈 Gráficos por status")
    st.bar_chart(resumo)

db.close()
    st.markdown("---")
   st.header("📤 Exportação Geral do Banco")

    # Consulta RCs
    requisicoes = db.query(Requisicao).all()
    df_rcs = pd.DataFrame([{
        "ID": r.id,
        "RC": r.rc,
        "Solicitação Senior": r.solicitacao_senior,
        "Empresa": r.empresa,
        "Filial": r.filial,
        "Data": r.data,
        "Status": r.status,
        "Responsável": r.responsavel,
        "Link": r.link,
        "Número OC": r.numero_oc
    } for r in requisicoes])

    # Consulta Usuários
    usuarios = db.query(Usuario).all()
    df_users = pd.DataFrame([{
        "ID": u.id,
        "Nome": u.nome,
        "Senha": u.senha,
        "Cargo": u.cargo,
        "Ativo": "Sim" if u.ativo else "Não"
    } for u in usuarios])

    # Gera arquivo .xlsx com múltiplas abas
    arquivo_excel = exportar_para_excel({
        "RCs": df_rcs,
        "Usuários": df_users
    })

    # Botão de download único
    st.download_button(
        label="📥 Baixar Relatório Completo (.xlsx)",
        data=arquivo_excel,
        file_name="relatorio_sistema_compras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.header("👤 Gerenciamento de Usuários")

    # --- Formulário de cadastro ---
    with st.form("form_novo_usuario"):
        nome = st.text_input("Nome de usuário")
        senha = st.text_input("Senha")
        cargo = st.selectbox("Cargo", ["comprador", "admin"])
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            existente = db.query(Usuario).filter_by(nome=nome).first()
            if existente:
                st.warning("Este nome de usuário já está em uso.")
            else:
                novo = Usuario(nome=nome, senha=senha, cargo=cargo, ativo=1)
                db.add(novo)
                db.commit()
                st.success("Usuário cadastrado com sucesso.")
                st.session_state["reload_admin"] = True

    usuarios = db.query(Usuario).all()
    for u in usuarios:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.write(f"**{u.nome}**")
        with col2:
            st.write(u.cargo)
        with col3:
            status = "✅ Ativo" if u.ativo else "❌ Inativo"
            st.write(status)
        with col4:
            if u.ativo:
                if st.button("Desativar", key=f"desativar_{u.id}"):
                    u.ativo = 0
                    db.commit()
                    st.success("Usuário desativado com sucesso.")
                    st.session_state["reload_admin"] = True

            else:
                if st.button("Ativar", key=f"ativar_{u.id}"):
                    u.ativo = 1
                    db.commit()
                    st.success("Usuário ativado com sucesso.")
                    st.session_state["reload_admin"] = True
        with col5:
            if st.button("Excluir", key=f"excluir_{u.id}"):
                db.delete(u)
                db.commit()
                st.success("Usuário cadastrado com sucesso.")
                st.session_state["reload_admin"] = True

        #criar uma opção de alterar a senha

    db.close()
