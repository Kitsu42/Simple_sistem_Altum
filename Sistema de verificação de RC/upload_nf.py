import streamlit as st
import os

def pagina_upload():
    st.title("📎 Upload de Arquivos")
    file = st.file_uploader("Enviar arquivo (NF, OC...)", type=["pdf", "jpg", "png"])
    if file:
        os.makedirs("uploads", exist_ok=True)
        with open(os.path.join("uploads", file.name), "wb") as f:
            f.write(file.read())
        st.success(f"{file.name} salvo com sucesso.")
