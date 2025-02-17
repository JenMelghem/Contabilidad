import tkinter as tk
from tkinter import ttk, filedialog
import csv
import pandas as pd
from fpdf import FPDF

# ------------------------
# Función para cargar CSV
# ------------------------
def load_csv(filename):
    """
    Carga un archivo CSV que contenga las columnas:
    'codigo','nombre','depreciaciones','total_cuenta','total_grupos'
    Retorna una lista de diccionarios.
    """
    accounts_data = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts_data.append(row)
    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado. Se cargará una lista vacía.")
    return accounts_data

# ------------------------
# Función para buscar
# ------------------------
def search_accounts(search_text, accounts_data):
    """
    Filtra la lista de cuentas (accounts_data) según el texto de búsqueda.
    Se compara con 'codigo' y con 'nombre' (ambos en minúsculas).
    Retorna una lista de diccionarios filtrados.
    """
    filtered = []
    search_lower = search_text.lower().strip()
    for account in accounts_data:
        codigo = account['codigo'].lower()
        nombre = account['nombre'].lower()
        if search_lower in codigo or search_lower in nombre:
            filtered.append(account)
    return filtered

# ------------------------
# Ventana principal
# ------------------------
def main_window(root, accounts_data):
    """
    Configura la ventana principal (Balance General).
    """
    root.title("Sistema de Contabilidad - BALANCE GENERAL")
    root.geometry("900x600")
    root.configure(bg="#BDC3C7")  # Color de fondo opcional

    # Frame superior para datos de Empresa, Año, Saldo
    frame_top = tk.Frame(root, bg="#BDC3C7")
    frame_top.pack(pady=10, fill='x')

    # Etiquetas y campos de entrada
    tk.Label(frame_top, text="Empresa:", bg="#BDC3C7").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_empresa = tk.Entry(frame_top, width=25)
    entry_empresa.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_top, text="Año:", bg="#BDC3C7").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_anio = tk.Entry(frame_top, width=10)
    entry_anio.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_top, text="Saldo:", bg="#BDC3C7").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    entry_saldo = tk.Entry(frame_top, width=10)
    entry_saldo.grid(row=0, column=5, padx=5, pady=5)

    # Combobox para elegir modo de PDF
    tk.Label(frame_top, text="Ver como:", bg="#BDC3C7").grid(row=0, column=6, padx=5, pady=5, sticky="e")
    view_options = ["Balance General", "Reporte"]
    var_view = tk.StringVar(value=view_options[0])
    combo_view = ttk.Combobox(frame_top, textvariable=var_view, values=view_options, state="readonly", width=15)
    combo_view.grid(row=0, column=7, padx=5, pady=5)

    # Frame para íconos (Exportar a Excel, Exportar a PDF)
    frame_icons = tk.Frame(root, bg="#BDC3C7")
    frame_icons.pack(pady=5, fill='x')

    # Carga de iconos (ajusta las rutas a tus iconos)
    try:
        excel_icon = tk.PhotoImage(file="excel_icon.png")
    except:
        # Si no existe el icono, creamos un "placeholder"
        excel_icon = None

    try:
        pdf_icon = tk.PhotoImage(file="pdf_icon.png")
    except:
        pdf_icon = None

    # Tabla (Treeview) para mostrar las cuentas
    columns = ("Código", "Cuenta", "Depreciaciones", "Total de cuenta", "Total de grupos")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    tree.pack(pady=10, fill='both', expand=True)

    # Encabezados
    tree.heading("Código", text="Código")
    tree.heading("Cuenta", text="Cuenta")
    tree.heading("Depreciaciones", text="Depreciaciones")
    tree.heading("Total de cuenta", text="Total de cuenta")
    tree.heading("Total de grupos", text="Total de grupos")

    # Ajustar ancho de columnas
    tree.column("Código", width=80)
    tree.column("Cuenta", width=200)
    tree.column("Depreciaciones", width=120)
    tree.column("Total de cuenta", width=120)
    tree.column("Total de grupos", width=120)

    # Frame inferior para Totales
    frame_bottom = tk.Frame(root, bg="#BDC3C7")
    frame_bottom.pack(pady=5, fill='x')

    tk.Label(frame_bottom, text="Total Activo:", bg="#BDC3C7").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    lbl_total_activo = tk.Label(frame_bottom, text="0.00", bg="#BDC3C7")
    lbl_total_activo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_bottom, text="Total Pasivo:", bg="#BDC3C7").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    lbl_total_pasivo = tk.Label(frame_bottom, text="0.00", bg="#BDC3C7")
    lbl_total_pasivo.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_bottom, text="Total Patrimonio:", bg="#BDC3C7").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    lbl_total_patrimonio = tk.Label(frame_bottom, text="0.00", bg="#BDC3C7")
    lbl_total_patrimonio.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    tk.Label(frame_bottom, text="Balance General:", bg="#BDC3C7").grid(row=0, column=6, padx=5, pady=5, sticky="e")
    lbl_balance_general = tk.Label(frame_bottom, text="0.00", bg="#BDC3C7")
    lbl_balance_general.grid(row=0, column=7, padx=5, pady=5, sticky="w")

    # ------------------------
    # Funciones de Exportación
    # ------------------------

    def get_treeview_data():
        """Obtiene la data actual del Treeview como lista de diccionarios."""
        data = []
        for item in tree.get_children():
            values = tree.item(item, "values")
            # Empaquetamos en un diccionario con las mismas llaves que en 'columns'
            # Ajusta según tus necesidades
            row_dict = {
                "Código": values[0],
                "Cuenta": values[1],
                "Depreciaciones": values[2],
                "Total de cuenta": values[3],
                "Total de grupos": values[4],
            }
            data.append(row_dict)
        return data

    def save_to_excel():
        """Convierte el contenido del Treeview en un archivo Excel."""
        data = get_treeview_data()
        if not data:
            return  # No hay datos para exportar

        # Convierte la lista de diccionarios en un DataFrame de pandas
        df = pd.DataFrame(data)

        # Dialogo para guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            df.to_excel(file_path, index=False)
            print(f"Archivo Excel guardado en: {file_path}")

    def export_to_pdf():
        """Convierte el contenido del Treeview en un archivo PDF."""
        data = get_treeview_data()
        if not data:
            return  # No hay datos para exportar

        # Obtenemos el modo seleccionado (Balance General o Reporte)
        modo = var_view.get()

        # Dialogo para guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # Crear el PDF con FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)

        # Título
        pdf.cell(0, 10, f"Sistema de Contabilidad - {modo}", ln=True, align="C")
        pdf.ln(5)

        # Encabezados de la tabla
        pdf.set_font("Arial", "B", 10)
        headers = ["Código", "Cuenta", "Depreciaciones", "Total de cuenta", "Total de grupos"]
        col_widths = [25, 50, 30, 30, 30]  # Ajusta anchos según tus datos
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="C")
        pdf.ln(8)

        # Filas de la tabla
        pdf.set_font("Arial", "", 9)
        for row in data:
            pdf.cell(col_widths[0], 8, str(row["Código"]), border=1)
            pdf.cell(col_widths[1], 8, str(row["Cuenta"]), border=1)
            pdf.cell(col_widths[2], 8, str(row["Depreciaciones"]), border=1, align="R")
            pdf.cell(col_widths[3], 8, str(row["Total de cuenta"]), border=1, align="R")
            pdf.cell(col_widths[4], 8, str(row["Total de grupos"]), border=1, align="R")
            pdf.ln(8)

        # Guarda el PDF
        pdf.output(file_path)
        print(f"Archivo PDF guardado en: {file_path}")

    # ------------------------
    # Botones de exportación
    # ------------------------
    btn_excel = tk.Button(frame_icons, text="Exportar Excel", image=excel_icon, compound="left",
                          command=save_to_excel, bg="#BDC3C7")
    btn_excel.pack(side=tk.LEFT, padx=10)

    btn_pdf = tk.Button(frame_icons, text="Exportar PDF", image=pdf_icon, compound="left",
                        command=export_to_pdf, bg="#BDC3C7")
    btn_pdf.pack(side=tk.LEFT, padx=10)

    # ------------------------
    # Buscador
    # ------------------------
    frame_search = tk.Frame(root, bg="#BDC3C7")
    frame_search.pack(pady=5, fill='x')

    tk.Label(frame_search, text="Buscador de cuentas:", bg="#BDC3C7").pack(side=tk.LEFT, padx=5)
    entry_search = tk.Entry(frame_search, width=30)
    entry_search.pack(side=tk.LEFT, padx=5)

    def on_search():
        text = entry_search.get()
        result = search_accounts(text, accounts_data)
        # Limpiar Treeview
        for row in tree.get_children():
            tree.delete(row)
        # Agregar resultados
        for account in result:
            tree.insert("", tk.END, values=(
                account['codigo'],
                account['nombre'],
                account['depreciaciones'],
                account['total_cuenta'],
                account['total_grupos']
            ))

    btn_search = tk.Button(frame_search, text="Buscar", command=on_search)
    btn_search.pack(side=tk.LEFT, padx=5)

    # (Opcional) Carga inicial de todas las cuentas
    for account in accounts_data:
        tree.insert("", tk.END, values=(
            account['codigo'],
            account['nombre'],
            account['depreciaciones'],
            account['total_cuenta'],
            account['total_grupos']
        ))

# ------------------------
# Ventana Splash
# ------------------------
def splash_screen(root, accounts_data):
    """
    Ventana de presentación que dura unos segundos
    antes de mostrar la ventana principal.
    """
    splash = tk.Toplevel()
    splash.title("Bienvenido")
    splash.geometry("400x200")
    splash.overrideredirect(True)  # Quita la barra de título

    # Centro la ventana en la pantalla
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (200 // 2)
    splash.geometry(f"400x200+{x}+{y}")

    lbl = tk.Label(splash, text="Sistema de Contabilidad\nBALANCE GENERAL", 
                   font=("Arial", 14), bg="#2C3E50", fg="white")
    lbl.pack(expand=True, fill='both')

    def close_splash():
        splash.destroy()         # Cierra la ventana de splash
        root.deiconify()         # Muestra la ventana principal (estaba oculta)
        main_window(root, accounts_data)  # Configura la ventana principal

    # Programamos el cierre del splash a los 3 segundos
    splash.after(3000, close_splash)

# ------------------------
# Programa principal
# ------------------------
if __name__ == "__main__":
    # Carga de datos desde CSV
    # Asegúrate de tener un archivo "catalogo_cuentas.csv" con 
    # cabeceras: codigo, nombre, depreciaciones, total_cuenta, total_grupos
    accounts_data = load_csv("balance.csv")

    root = tk.Tk()
    root.withdraw()  # Ocultamos la ventana principal al inicio

    splash_screen(root, accounts_data)

    root.mainloop()
