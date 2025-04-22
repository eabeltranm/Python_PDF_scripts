import pdfplumber
import pandas as pd

PDF_file = "C:\\Users\\eabeltranm\\Documents\\Amor\\proceso_assut_europe\\Consulta registros sanitarios _ INVIMA_1.pdf"

with pdfplumber.open(PDF_file) as pdf:
    first_page = pdf.pages[0]
    tables_on_page = first_page.extract_tables({
        'vertical_strategy': 'lines',
        'horizontal_strategy': 'lines',
        'intersection_x_tolerance': 5,
        'intersection_y_tolerance': 5,
        'snap_tolerance': 3,
        'join_tolerance': 2,
        'edge_min_length': 5,
        'min_words_vertical': 2,
        'min_words_horizontal': 2,
    })
    
    for table in tables_on_page:
        if table:
            df = pd.DataFrame(table)
            print(df)