#reports/gerar_pdf.py
from fpdf import FPDF

def gerar_relatorio_pdf(df, caminho="relatorio.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Produtividade", ln=1, align="C")

    for i, row in df.iterrows():
        linha = f"{row['usuario']} | {row['status']} | {row['data']}"
        pdf.cell(200, 10, txt=linha, ln=1)

    pdf.output(caminho)
    return caminho
