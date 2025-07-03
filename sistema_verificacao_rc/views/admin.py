# views/admin.py
import streamlit as st
from banco import SessionLocal
from models import Usuario

def exibir():
    if st.session_state.get("cargo") != "admin":
        st.error("Acesso restrito.")
        return

    st.title("👥 Administração de Usuários")
    db = SessionLocal()

    # --- Formulário de cadastro ---
    st.subheader("➕ Cadastrar novo usuário")
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
                st.experimental_rerun()

    # --- Listagem e controle de usuários ---
    st.subheader("👤 Usuários cadastrados")
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
                    st.experimental_rerun()
            else:
                if st.button("Ativar", key=f"ativar_{u.id}"):
                    u.ativo = 1
                    db.commit()
                    st.experimental_rerun()
        with col5:
            if st.button("Excluir", key=f"excluir_{u.id}"):
                db.delete(u)
                db.commit()
                st.experimental_rerun()

    db.close()
