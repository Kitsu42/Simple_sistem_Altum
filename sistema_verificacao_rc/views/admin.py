# views/admin.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import joinedload

# Imports do app
from banco import SessionLocal
from models import Usuario, Requisicao, Empresa, Filial

# Import robusto do parser de planilhas (pacote ou script)
try:
    from sistema_verificacao_rc.planilhas import parse_backlog_excel, importar_backlog, as_display_br
except ImportError:
    from planilhas import parse_backlog_excel, importar_backlog, as_display_br

# Status helpers
from utils import (
    STATUS_BACKLOG,
    STATUS_EM_COTACAO,
    STATUS_FINALIZADO,
    dias_em_aberto,
)

# ------------------------------------------------------------------
# Exportador XLSX multi-aba
# ------------------------------------------------------------------
def exportar_para_excel(dfs: dict) -> bytes:
    """
    Recebe dict {nome_aba: DataFrame} e devolve bytes de um arquivo .xlsx
    com cada DataFrame em uma aba.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nome_aba, df in dfs.items():
            # Limpa strings para não quebrar linhas
            df_clean = df.applymap(
                lambda x: str(x).replace("\n", " ").strip() if isinstance(x, str) else x
            )
            df_clean.to_excel(writer, sheet_name=nome_aba, index=False)
    return output.getvalue()


# ------------------------------------------------------------------
# DataFrame com TODAS as requisições (para exportação)
# ------------------------------------------------------------------
def _carrega_df_requisicoes(db):
    """
    Carrega todas as RCs do banco e devolve DataFrame pronto para exportação.
    Inclui campos novos (data_prevista, solicitante, observacoes) se existirem.
    """
    rcs = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .all()
    )
    rows = []
    for r in rcs:
        rows.append({
            "Status": r.status,
            "RC": r.rc,
            "Solicitação Senior": r.solicitacao_senior,
            "Responsável": r.responsavel,
            "Número OC": r.numero_oc,            
            "Empresa": r.empresa_display,   # <-- property segura
            "Filial": r.filial_display,     # <-- property segura
            "Data Cadastro": r.data,
            "Data Prevista": getattr(r, "data_prevista", None),
            "Solicitante": getattr(r, "solicitante", None),
            "Observações": getattr(r, "observacoes", None),
            "Link": r.link,
        })
    df = pd.DataFrame(rows)

    # Formatação opcional BR para exportar — mantenho datas em ISO para Excel
    # df = as_display_br(df, cols=("Data Cadastro", "Data Prevista"))

    return df


# ------------------------------------------------------------------
# VIEW PRINCIPAL
# ------------------------------------------------------------------
def exibir():
    # --------------------------------------------------------------
    # Proteção de acesso
    # --------------------------------------------------------------
    if st.session_state.get("cargo") != "admin":
        st.error("Acesso restrito.")
        return

    # --------------------------------------------------------------
    # Rerun forçado pós-ação
    # --------------------------------------------------------------
    if st.session_state.get("reload_admin"):
        st.session_state["reload_admin"] = False
        st.rerun()
        return

    st.title("👥 Administração do Sistema")
    db = SessionLocal()

    # ==============================================================
    # IMPORTAÇÃO DE BACKLOG (Excel)
    # ==============================================================
    st.header("📤 Importar Backlog (Excel)")
    arquivo = st.file_uploader("Selecione o arquivo de backlog", type=["xlsx"])
    df_backlog = None
    if arquivo:
        arquivo.seek(0)
        try:
            df_backlog = parse_backlog_excel(arquivo)
            st.write(f"{len(df_backlog)} RC(s) encontradas no arquivo.")
            # Preview formatado BR para o usuário
            st.dataframe(as_display_br(df_backlog).head(40))
        except Exception as e:
            st.error(f"Falha ao ler o arquivo: {e}")
            df_backlog = None

        if df_backlog is not None and not df_backlog.empty:
            if st.button("Importar RCs para o Sistema"):
                novos = importar_backlog(df_backlog, db)  # retorna int
                st.success(f"{novos} nova(s) RC(s) adicionadas ao backlog.")
                st.session_state["reload_admin"] = True
                db.close()
                st.rerun()
                return

    # ==============================================================
    # RELATÓRIOS DE ATIVIDADE
    # ==============================================================
    st.header("📊 Relatórios de Atividade")

    requisicoes = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .filter(Requisicao.responsavel != None)  # noqa: E711
        .all()
    )

    if not requisicoes:
        st.info("Nenhuma RC registrada com responsável definido.")
    else:
        # Monta DF base para análise
        df = pd.DataFrame([{
            "responsavel": r.responsavel,
            "status": r.status,
            "data": r.data,
            "empresa": r.empresa_display,   # CORRIGIDO
            "filial": r.filial_display,     # CORRIGIDO
        } for r in requisicoes])

        # Converte data (safe BR)
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
        df["dias_em_aberto"] = (pd.Timestamp.today().normalize() - df["data"]).dt.days

        # Agregações
        em_cotacao = df[df["status"] == STATUS_EM_COTACAO].groupby("responsavel").size().rename("Em Cotação")
        finalizadas = df[df["status"] == STATUS_FINALIZADO].groupby("responsavel").size().rename("Finalizadas")
        backlog_counts = df[df["status"] == STATUS_BACKLOG].groupby("responsavel").size().rename("Backlog")
        em_cot_prazo = (
            df[(df["status"] == STATUS_EM_COTACAO) & (df["dias_em_aberto"] <= 10)]
            .groupby("responsavel")
            .size()
            .rename("Em cotação - no prazo")
        )

        resumo = pd.concat([backlog_counts, em_cotacao, em_cot_prazo, finalizadas], axis=1).fillna(0).astype(int)
        resumo = resumo.sort_values(by=["Finalizadas"], ascending=False)

        st.subheader("📌 Resumo por usuário")
        st.dataframe(resumo)

        st.subheader("📈 Comparativo (Backlog / Cotação / No Prazo / Finalizadas)")
        st.bar_chart(resumo)

        st.subheader("🥧 RCs por Usuário")
        rcs_por_usuario = df["responsavel"].value_counts().reset_index()
        rcs_por_usuario.columns = ["Responsável", "Total RCs"]
        fig_pizza = px.pie(
            rcs_por_usuario,
            names="Responsável",
            values="Total RCs",
            hole=0.3,
            title="Distribuição de RCs por Usuário"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

        st.subheader("📊 RCs Atrasadas (>10 dias)")
        df_atraso = df[(df["status"] == STATUS_EM_COTACAO) & (df["dias_em_aberto"] > 10)]
        if df_atraso.empty:
            st.info("Nenhuma RC em atraso superior a 10 dias.")
        else:
            st.dataframe(df_atraso[["empresa", "filial", "responsavel", "dias_em_aberto"]])
            grp = (
                df_atraso
                .groupby(["empresa", "filial", "responsavel"])
                .size()
                .reset_index(name="RCs Atrasadas")
            )
            cor = st.color_picker("Escolha a cor das barras", value="#636EFA")
            fig_barra = go.Figure(data=[
                go.Bar(
                    x=grp.apply(lambda row: f"{row['empresa']} - {row['filial']}\n{row['responsavel']}", axis=1),
                    y=grp["RCs Atrasadas"],
                    marker_color=cor,
                    text=grp["RCs Atrasadas"],
                    textposition='auto'
                )
            ])
            fig_barra.update_layout(title="RCs em Atraso (>10 dias)", xaxis_tickangle=-45)
            st.plotly_chart(fig_barra, use_container_width=True)

    # ==============================================================
    # EXPORTAÇÃO
    # ==============================================================
    st.markdown("---")
    st.header("📄 Exportação Geral do Banco")

    df_rcs = _carrega_df_requisicoes(db)
    usuarios = db.query(Usuario).all()
    df_users = pd.DataFrame([{
        "ID": u.id,
        "Nome": u.nome,
        "Cargo": u.cargo,
        "Ativo": "Sim" if u.ativo else "Não",
    } for u in usuarios])

    arquivo_excel = exportar_para_excel({"RCs": df_rcs, "Usuários": df_users})

    st.download_button(
        label="📅 Baixar Relatório Completo (.xlsx)",
        data=arquivo_excel,
        file_name="relatorio_sistema_compras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ==============================================================
    # GERENCIAMENTO DE USUÁRIOS
    # ==============================================================
    st.markdown("---")
    st.header("👤 Gerenciamento de Usuários")

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
                st.rerun()
                return

    usuarios = db.query(Usuario).all()
    for u in usuarios:
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2])
        with col1:
            st.write(f"**{u.nome}**")
        with col2:
            st.write(u.cargo)
        with col3:
            st.write("✅ Ativo" if u.ativo else "❌ Inativo")
        with col4:
            if u.ativo:
                if st.button("Desativar", key=f"desativar_{u.id}"):
                    u.ativo = 0
                    db.commit()
                    st.success("Usuário desativado com sucesso.")
                    st.session_state["reload_admin"] = True
                    st.rerun()
                    return
            else:
                if st.button("Ativar", key=f"ativar_{u.id}"):
                    u.ativo = 1
                    db.commit()
                    st.success("Usuário ativado com sucesso.")
                    st.session_state["reload_admin"] = True
                    st.rerun()
                    return
        with col5:
            if st.button("Excluir", key=f"excluir_{u.id}"):
                db.delete(u)
                db.commit()
                st.success("Usuário excluído com sucesso.")
                st.session_state["reload_admin"] = True
                st.rerun()
                return
        with col6:
            nova_senha = st.text_input("Nova senha", key=f"senha_{u.id}", type="password")
            if st.button("Alterar Senha", key=f"altsenha_{u.id}"):
                if nova_senha.strip():
                    u.senha = nova_senha
                    db.commit()
                    st.success("Senha alterada com sucesso.")
                    st.session_state["reload_admin"] = True
                    st.rerun()
                    return
                else:
                    st.warning("Digite uma nova senha antes de confirmar a alteração.")

    db.close()
