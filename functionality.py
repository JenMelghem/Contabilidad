import csv
import pandas as pd
from fpdf import FPDF
from tkinter import filedialog

def load_csv(filename):
    accounts_data = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts_data.append(row)
    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado. Se cargará una lista vacía.")
    return accounts_data

def search_accounts(search_text, accounts_data):
    filtered = []
    search_lower = search_text.lower().strip()
    for account in accounts_data:
        codigo = account['codigo'].lower()
        nombre = account['nombre'].lower()
        if search_lower in codigo or search_lower in nombre:
            filtered.append(account)
    return filtered

def save_to_excel(data):
    """
    Convierte la lista de diccionarios 'data' en un archivo Excel.
    """
    if not data:
        return
    df = pd.DataFrame(data)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if file_path:
        df.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {file_path}")

def export_to_pdf(data, modo):
 
    if not data:
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if not file_path:
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Sistema de Contabilidad - {modo}", ln=True, align="C")
    pdf.ln(5)

    # Encabezados de la tabla
    pdf.set_font("Arial", "B", 10)
    headers = ["Código", "Cuenta", "Depreciaciones", "Dep+csinDep", "Total de cuenta", "Total de grupos"]
    col_widths = [25, 50, 30, 30, 30, 30]  # Ajusta según necesites
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align="C")
    pdf.ln(8)

    # Filas de datos
    pdf.set_font("Arial", "", 9)
    for row in data:
        pdf.cell(col_widths[0], 8, str(row["codigo"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["nombre"]), border=1)
        pdf.cell(col_widths[2], 8, str(row["depreciaciones"]), border=1, align="R")
        pdf.cell(col_widths[3], 8, str(row["Dep+csinDep"]), border=1, align="R")
        pdf.cell(col_widths[4], 8, str(row["total_cuenta"]), border=1, align="R")
        pdf.cell(col_widths[5], 8, str(row["total_grupos"]), border=1, align="R")
        pdf.ln(8)

    pdf.output(file_path)
    print(f"Archivo PDF guardado en: {file_path}")