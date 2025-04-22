import pdfplumber
import pandas as pd

with pdfplumber.open("C:\\Users\\eabeltranm\\Documents\\Amor\\Nuevo_proceso\\invima_1.pdf") as pdf:
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
        'keep_blank_chars': True
    })
    for table in tables_on_page:
        df = pd.DataFrame(table)
        print(df)