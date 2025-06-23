import pandas as pd

def validar_planilha(excel_file):
    try:
        xls = pd.ExcelFile(excel_file)
        aba = xls.sheet_names[0]
        df = pd.read_excel(excel_file, sheet_name=aba)

        colunas_necessarias = ['Nº SC', 'DATA SC', 'OBSERVAÇÃO']
        if not all(col in df.columns for col in colunas_necessarias):
            return {"erro": "A planilha precisa conter as colunas: Nº SC, DATA SC e OBSERVAÇÃO"}, 400

        df['Nº SC'] = df['Nº SC'].astype(str)
        df['DATA SC'] = pd.to_datetime(df['DATA SC'], errors='coerce')
        df['OBSERVAÇÃO'] = df['OBSERVAÇÃO'].fillna('')

        agrupado = df.groupby('Nº SC').agg({
            'DATA SC': 'first',
            'OBSERVAÇÃO': 'first',
            'Nº SC': 'count'
        }).rename(columns={'Nº SC': 'Qtd Linhas'}).reset_index()

        resultado = agrupado.to_dict(orient='records')
        return {"dados": resultado}, 200

    except Exception as e:
        return {"erro": f"Erro ao processar planilha: {str(e)}"}, 500
