# views/admin.py
import streamlit as st
import pandas as pd
from banco import SessionLocal
from models import Usuario, Requisicao, Empresa, Filial
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    STATUS_BACKLOG,
    STATUS_EM_COTACAO,
    STATUS_FINALIZADO,
    dias_em_aberto,
    parse_backlog_xml,
    parse_backlog_excel,
    limpa_cnpj,
)


# ------------------------------------------------------------------
# Exportador XLSX multi-aba
# ------------------------------------------------------------------
def exportar_para_excel(dfs: dict) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nome_aba, df in dfs.items():
            df_clean = df.applymap(lambda x: str(x).replace("\n", " ").strip() if isinstance(x, str) else x)
            df_clean.to_excel(writer, sheet_name=nome_aba, index=False)
    return output.getvalue()


# ------------------------------------------------------------------
# DataFrame com TODAS as requisições (para exportação)
# ------------------------------------------------------------------
def _carrega_df_requisicoes(db):
    rcs = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .all()
    )
    rows = []
    for r in rcs:
        rows.append({
            "ID": r.id,
            "RC": r.rc,
            "Solicitação Senior": r.solicitacao_senior,
            "Empresa": r.empresa_display,
            "Filial": r.filial_display,
            "Data": r.data,
            "Status": r.status,
            "Responsável": r.responsavel,
            "Link": r.link,
            "Número OC": r.numero_oc,
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Importa RCs do DataFrame de backlog
# ------------------------------------------------------------------
def importar_backlog(df: pd.DataFrame, db) -> dict:
    """
    Insere RCs do DataFrame no banco como STATUS_BACKLOG.
    Evita duplicar RC (chave: campo 'rc').
    Tenta vincular a Filial por CNPJ; fallback: mantém somente texto.
    Retorna dict com contagens.
    """
    # Pré-carrega filiais por CNPJ (apenas dígitos)
    filiais = db.query(Filial).options(joinedload(Filial.empresa)).all()
    filiais_por_cnpj = {limpa_cnpj(f.cnpj): f for f in filiais if f.cnpj}

    novos = 0
    ja_existia = 0
    vinculadas_filial = 0
    sem_cnpj = 0
    sem_match = 0

    # Normaliza colunas (df veio do parse_backlog_excel)
    # garantias: rc, solicitacao_senior, data_cadastro, filial_raw, Filial_CNPJ, Filial_Nome etc.
    cols = {c.lower(): c for c in df.columns}

    def get(row, logical):
        c = cols.get(logical.lower())
        if c:
            return row[c]
        return row.get(logical, "")

    for _, row in df.iterrows():
        rc_num = str(get(row, "rc")).strip()
        if not rc_num:
            continue

        # já existe?
        if db.query(Requisicao).filter_by(rc=rc_num).first():
            ja_existia += 1
            continue

        sc_val = str(get(row, "solicitacao_senior") or "").strip()

        emp_txt = ""  # derivaremos da filial se encontrarmos; fica vazio/legado caso contrário
        fil_raw = str(get(row, "filial_raw") or "").strip()
        fil_cnpj = limpa_cnpj(row.get("Filial_CNPJ", "")) if "Filial_CNPJ" in df.columns else ""
        fil_nome = str(row.get("Filial_Nome", "")).strip() if "Filial_Nome" in df.columns else ""

        # Data de cadastro
        data_cad = row.get("data_cadastro")
        if pd.isna(data_cad):
            data_py = None
        else:
            # se vier como Timestamp -> .date(); se string -> to_datetime
            if isinstance(data_cad, pd.Timestamp):
                data_py = data_cad.date()
            else:
                dt = pd.to_datetime(data_cad, errors="coerce")
                data_py = None if pd.isna(dt) else dt.date()

        # Data prevista (não salva no modelo atual; guardamos em link? ignoramos)
        # TODO: criar coluna futura

        # Observações / Usuário (modelo ainda não tem campos; ignoramos por ora)
        link_val = str(get(row, "link") or "").strip()

        # Monta RC
        r = Requisicao(
            rc=rc_num,
            solicitacao_senior=sc_val,
            empresa_txt=emp_txt,
            filial_txt=fil_nome or fil_raw,
            data=data_py,
            status=STATUS_BACKLOG,
            link=link_val,
        )

        # Vincula filial se possível
        if fil_cnpj:
            f = filiais_por_cnpj.get(fil_cnpj)
            if f:
                r.filial_id = f.id
                r.empresa_txt = f.empresa.nome  # para histórico textual
                vinculadas_filial += 1
            else:
                sem_match += 1
        else:
            sem_cnpj += 1

        db.add(r)
        novos += 1

    if novos:
        db.commit()

    return {
        "novos": novos,
        "ja_existia": ja_existia,
        "vinculadas_filial": vinculadas_filial,
        "sem_cnpj": sem_cnpj,
        "sem_match": sem_match,
    }


# ------------------------------------------------------------------
# VIEW PRINCIPAL
# ------------------------------------------------------------------
def exibir():
    # reload externo (de import ou ações)
    if st.session_state.get("reload_admin"):
        st.session_state["reload_admin"] = False
        st.rerun()
        return

    if st.session_state.get("cargo") != "admin":
        st.error("Acesso restrito.")
        return

    st.title("👥 Administração do Sistema")
    db = SessionLocal()

    # ==============================================================
    # IMPORTAÇÃO DE BACKLOG (XML ou Excel)
    # ==============================================================
    st.header("📤 Importar Backlog (XML ou Excel)")
    arquivo = st.file_uploader("Selecione o arquivo de backlog", type=["xml", "xlsx"])
    df_backlog = None
    if arquivo:
        arquivo.seek(0)
        if arquivo.name.lower().endswith(".xml"):
            try:
                df_backlog = parse_backlog_xml(arquivo)
                st.write(f"{len(df_backlog)} RCs encontradas no XML.")
            except Exception as e:
                st.error(str(e))
        else:
            try:
                df_backlog = parse_backlog_excel(arquivo)
                st.write(f"{len(df_backlog)} RCs encontradas no Excel.")
            except Exception as e:
                st.error(str(e))

        if df_backlog is not None and not df_backlog.empty:
            st.dataframe(df_backlog.head(40))
            if st.button("Importar RCs para o Sistema"):
                stats = importar_backlog(df_backlog, db)
                st.success(
                    f"{stats['novos']} novas RCs inseridas. "
                    f"{stats['ja_existia']} ignoradas (já existiam). "
                    f"{stats['vinculadas_filial']} vinculadas à filial cadastral."
                )
                if stats["sem_match"]:
                    st.warning(f"{stats['sem_match']} RCs não foram vinculadas (CNPJ não encontrado).")
                st.session_state["reload_admin"] = True
                db.close()
                st.rerun()
                return

    # ==============================================================
    # RELATÓRIOS
    # ==============================================================
    st.header("📊 Relatórios de Atividade")

    requisicoes = (
        db.query(Requisicao)
        .options(joinedload(Requisicao.filial_obj).joinedload(Filial.empresa))
        .filter(Requisicao.responsavel != None)
        .all()
    )

    if not requisicoes:
        st.info("Nenhuma RC registrada com responsável definido.")
    else:
        df = pd.DataFrame([{
            "responsavel": r.responsavel,
            "status": r.status,
            "data": r.data,
            "empresa": r.empresa_display,
            "filial": r.filial_display,
        } for r in requisicoes])

        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df["dias_em_aberto"] = (pd.to_datetime("today") - df["data"]).dt.days

        em_cotacao = df[df["status"] == STATUS_EM_COTACAO].groupby("responsavel").size().rename("Em Cotação")
        finalizadas = df[df["status"] == STATUS_FINALIZADO].groupby("responsavel").size().rename("Finalizadas")
        backlog = df[df["status"] == STATUS_BACKLOG].groupby("responsavel").size().rename("Backlog")
        em_cot_prazo = df[(df["status"] == STATUS_EM_COTACAO) & (df["dias_em_aberto"] <= 10)].groupby("responsavel").size().rename("Em cotação - no prazo")

        resumo = pd.concat([backlog, em_cotacao, em_cot_prazo, finalizadas], axis=1).fillna(0).astype(int)
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
