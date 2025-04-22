import pdfplumber
import pandas as pd

with pdfplumber.open("C:\\Users\\eabeltranm\\Documents\\Amor\\Nuevo_proceso\\invima_1.pdf") as pdf:
    first_page = pdf.pages[0]
    tables = first_page.extract_tables({'vertical_strategy':'lines',
                                        'horizontal_strategy':'lines',
                                        'intersection_x_tolerance':10,
                                        'intersection_y_tolerance':10
                                        })
    for table in tables:
        df = pd.DataFrame(table)
        print(df)