# excel_model.py
import pandas as pd
from openpyxl import load_workbook

class ExcelModel:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_sheet(self, sheet_name):
        # Cargar el archivo Excel y devolver la hoja deseada
        return pd.read_excel(self.file_path, sheet_name=sheet_name)

    def save_data(self, sheet_name, data):
        # Cargar el archivo Excel
        wb = load_workbook(self.file_path)
        sheet = wb[sheet_name]

        # Escribir los datos en la siguiente fila disponible
        max_row = sheet.max_row + 1
        for col, value in enumerate(data, start=1):
            sheet.cell(row=max_row, column=col).value = value
        
        wb.save(self.file_path)  # Guardar el archivo

