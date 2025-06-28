import streamlit as st
from database import SessionLocal
from models import RC
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def exportar_pdf(rcs):
    path = "reports/relatorio.pdf"
    os.makedirs("reports", exist_ok=True)
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Relatório de RCs")
    y -= 30
    c.setFont("Helvetica", 10)
    for rc in rcs:
        if y < 80:
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"SC: {rc.numero_sc} | Status: {rc.status} | Resp: {rc.responsavel or '--'} | OC: {rc.numero_oc or '--'}")
        y -= 20
    c.save()
    return path

def pagina_pdf():
    st.title("🖨️ Gerar PDF de RCs")
    db = SessionLocal()
    rcs = db.query(RC).all()
    if st.button("Gerar PDF"):
        pdf_path = exportar_pdf(rcs)
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Baixar PDF", f, file_name="relatorio_rcs.pdf")
    db.close()
