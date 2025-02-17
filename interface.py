import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, PhotoImage
import csv

# ---------------------------------------
# Función para cargar datos (CSV o dummy)
# ---------------------------------------
def load_csv(filename):
    accounts_data = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts_data.append(row)
    except Exception as e:
        print("No se encontró el CSV.")
    return accounts_data

# ------------------------------
# Pantalla principal (Interfaz)
# ------------------------------
def main_window(root, accounts_data, company_name, year):
    root.title("Sistema de Contabilidad")
    root.geometry("900x600")
    root.configure(bg="#88a1b3")

    # Diccionario para almacenar los saldos ingresados
    saldos_guardados = {}

    # --- Frame Superior: Información de la Empresa ---
    frame_top = tk.Frame(root, bg="#BDC3C7")
    frame_top.pack(fill='x', padx=10, pady=10)
    
    # Información (títulos) centrados en tres líneas
    tk.Label(frame_top, text=f"{company_name}", bg="#BDC3C7", font=("Arial", 16, "bold"),
             justify="center").pack(pady=2)
    tk.Label(frame_top, text="Balance General", bg="#BDC3C7", font=("Arial", 16, "bold"),
             justify="center").pack(pady=2)
    tk.Label(frame_top, text=f"AL 31 de diciembre del {year}", bg="#BDC3C7", font=("Arial", 16, "bold"),
             justify="center").pack(pady=2)
    
    # --- Frame para el buscador y el saldo (parte superior del área de la tabla) ---
    frame_search_table = tk.Frame(root, bg="#BDC3C7")
    frame_search_table.pack(fill="x", padx=10, pady=(5,0))
    
    # Buscar
    tk.Label(frame_search_table, text="Buscar:", bg="#BDC3C7", font=("Arial", 10)).pack(side="left", padx=5)
    entry_search = tk.Entry(frame_search_table, width=30)
    entry_search.pack(side="left", padx=5)
    
    # Saldo
    tk.Label(frame_search_table, text="Saldo:", bg="#BDC3C7", font=("Arial", 12)).pack(side="left", padx=5)
    entry_saldo = tk.Entry(frame_search_table, width=20)
    entry_saldo.pack(side="left", padx=5)

    # --- Frame para el Treeview (Catálogo de Cuentas) ---
    frame_tree = tk.Frame(root, bg="#BDC3C7")
    frame_tree.pack(padx=10, pady=5, fill='both', expand=True)
    
    columns = ("Código", "Cuenta", "Depreciaciones", "Dep+csinDep", "Total de cuenta", "Total de grupos")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
    tree.pack(fill='both', expand=True)
    
    for col in columns:
        tree.heading(col, text=col)
        if col == "Código":
            tree.column(col, width=80)
        elif col == "Cuenta":
            tree.column(col, width=200)
        else:
            tree.column(col, width=120)
    
    def update_tree(data):
        for item in tree.get_children():
            tree.delete(item)
        for account in data:
            # Verificar si la cuenta tiene un saldo guardado
            codigo = account["codigo"]
            saldo_depreciaciones = saldos_guardados.get(codigo, {}).get("Depreciaciones", "")
            saldo_dep_csin_dep = saldos_guardados.get(codigo, {}).get("Dep+csinDep", "")
            
            # Insertar la cuenta en la tabla con los saldos guardados
            tree.insert("", "end", values=(
                codigo,
                account["nombre"],
                saldo_depreciaciones,
                saldo_dep_csin_dep,
                account["total_cuenta"],
                account["total_grupos"]
            ))

    # Función para manejar la entrada de saldos
    def handle_saldo_entry():
        saldo = entry_saldo.get().strip()
        if not saldo:
            messagebox.showerror("Error", "Por favor, ingrese un saldo.")
            return
        
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor, seleccione una cuenta.")
            return
        
        # Obtener el código de la cuenta seleccionada
        codigo = tree.item(selected_item, "values")[0]
        
        # Determinar la columna correcta
        columna = None
        if codigo in ["1.1.3.1", "1.2.2.2", "1.2.2.3", "1.2.2.4", "1.2.2.5", "1.2.2.6", "1.2.2.7", "1.2.2.8"] or len(codigo.split('.')) == 5:
            columna = "Depreciaciones"
        elif len(codigo.split('.')) == 4:
            columna = "Dep+csinDep"
        
        if columna is None:
            messagebox.showerror("Error", "No se puede asignar un saldo a esta cuenta.")
            return
        
        #Guardar el saldo en el diccionario
        if codigo not in saldos_guardados:
            saldos_guardados[codigo] = {}
        saldos_guardados[codigo][columna] = saldo
        
        # Actualizar la tabla
        on_search()

        # Actualizar datos en memoria y la tabla
        for account in accounts_data:
            if account["codigo"] == codigo:
                account[columna] = saldo
                break

        values = list(tree.item(selected_item, "values"))
        if columna == "Depreciaciones":
            values[2] = saldo
        elif columna == "Dep+csinDep":
            values[3] = saldo
        tree.item(selected_item, values=values)
        
        
        # Recalcular totales
        calcular_totales()
    
    # Botón para ingresar saldo
    btn_ingresar_saldo = tk.Button(frame_search_table, text="Ingresar Saldo", command=handle_saldo_entry)
    btn_ingresar_saldo.pack(side="left", padx=5)
    
    # Función para calcular totales
    def calcular_totales():
        total_activo_corriente = 0
        total_activo_no_corriente = 0
        total_pasivo_corriente = 0
        total_pasivo_no_corriente = 0
        
        for item in tree.get_children():
            values = tree.item(item, "values")
            codigo = values[0]
            saldo = float(values[3]) if values[3] else 0
            
            if codigo.startswith("0.1.1"):
                total_activo_corriente += saldo
            elif codigo.startswith("0.1.2"):
                total_activo_no_corriente += saldo
            elif codigo.startswith("0.2.1"):
                total_pasivo_corriente += saldo
            elif codigo.startswith("0.2.2"):
                total_pasivo_no_corriente += saldo
        
        # Actualizar totales en la interfaz
        lbl_total_activo.config(text=f"{total_activo_corriente + total_activo_no_corriente:.2f}")
        lbl_total_pasivo.config(text=f"{total_pasivo_corriente + total_pasivo_no_corriente:.2f}")
        lbl_total_patrimonio.config(text="0.00")  # Aquí debes agregar la lógica para calcular el patrimonio
        lbl_balance_general.config(text=f"{total_activo_corriente + total_activo_no_corriente:.2f}")

    
    # Función de búsqueda automática
    def on_search(event=None):
        search_text = entry_search.get().lower().strip()
        filtered = []
        for account in accounts_data:
            # Buscar por código (sin puntos) o por nombre
            codigo_sin_puntos = account["codigo"].replace(".", "").lower()
            nombre = account["nombre"].lower()
            if (search_text in codigo_sin_puntos) or (search_text in nombre):
                filtered.append(account)
        update_tree(filtered)
    
    # Vincular la búsqueda automática al evento KeyRelease
    entry_search.bind("<KeyRelease>", on_search)
    
    # Cargar datos iniciales
    update_tree(accounts_data)
    
    # --- Frame Inferior: Totales y Botones de Exportación ---
    frame_bottom = tk.Frame(root, bg="#BDC3C7")
    frame_bottom.pack(fill='x', padx=10, pady=10)
    
    # Frame para Totales (a la izquierda)
    frame_totals = tk.Frame(frame_bottom, bg="#BDC3C7")
    frame_totals.pack(side="left", fill="x", expand=True)
    
    tk.Label(frame_totals, text="Total Activo:", bg="#BDC3C7").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    lbl_total_activo = tk.Label(frame_totals, text="0.00", bg="#BDC3C7")
    lbl_total_activo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    tk.Label(frame_totals, text="Total Pasivo:", bg="#BDC3C7").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    lbl_total_pasivo = tk.Label(frame_totals, text="0.00", bg="#BDC3C7")
    lbl_total_pasivo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    
    tk.Label(frame_totals, text="Total Patrimonio:", bg="#BDC3C7").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    lbl_total_patrimonio = tk.Label(frame_totals, text="0.00", bg="#BDC3C7")
    lbl_total_patrimonio.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    
    tk.Label(frame_totals, text="Balance General:", bg="#BDC3C7").grid(row=0, column=6, padx=5, pady=5, sticky="e")
    lbl_balance_general = tk.Label(frame_totals, text="0.00", bg="#BDC3C7")
    lbl_balance_general.grid(row=0, column=7, padx=5, pady=5, sticky="w")
    
    # Frame para los botones de Exportación (a la derecha)
    frame_buttons = tk.Frame(frame_bottom, bg="#BDC3C7")
    frame_buttons.pack(side="right")
    
    try:
        excel_icon = PhotoImage(file="pngs/excel_icon.png")
    except Exception as e:
        print("No se encontró excel_icon.png, se usará texto.")
        excel_icon = None

    try:
        pdf_icon = PhotoImage(file="pngs/pdf_icon.png")
    except Exception as e:
        print("No se encontró pdf_icon.png, se usará texto.")
        pdf_icon = None

    def export_excel():
        messagebox.showinfo("Exportar a Excel", "Simulación de exportación a Excel.")
    
    btn_excel = tk.Button(frame_buttons, command=export_excel, bg="#BDC3C7", bd=0)
    if excel_icon is not None:
        btn_excel.config(image=excel_icon)
        btn_excel.image = excel_icon  # Para mantener la referencia
    else:
        btn_excel.config(text="Excel")
    btn_excel.pack(side="left", padx=10)
    
    def export_pdf():
        pdf_options = Toplevel(root)
        pdf_options.title("Exportar a PDF - Ver como")
        pdf_options.geometry("300x150")
        pdf_options.configure(bg="#BDC3C7")
        
        tk.Label(pdf_options, text="Ver como:", bg="#BDC3C7", font=("Arial", 12)) \
            .pack(pady=10)
        option_var = tk.StringVar(value="Balance General")
        rb1 = tk.Radiobutton(pdf_options, text="Balance General", variable=option_var,
                             value="Balance General", bg="#BDC3C7")
        rb1.pack(anchor="w", padx=20)
        rb2 = tk.Radiobutton(pdf_options, text="Reporte", variable=option_var,
                             value="Reporte", bg="#BDC3C7")
        rb2.pack(anchor="w", padx=20)
        
        def confirm_pdf():
            selected_option = option_var.get()
            pdf_options.destroy()
            messagebox.showinfo("Exportar a PDF", f"Simulación de exportación a PDF con diseño: {selected_option}")
        
        btn_confirm = tk.Button(pdf_options, text="Exportar", command=confirm_pdf)
        btn_confirm.pack(pady=10)
    
    btn_pdf = tk.Button(frame_buttons, command=export_pdf, bg="#BDC3C7", bd=0)
    if pdf_icon is not None:
        btn_pdf.config(image=pdf_icon)
        btn_pdf.image = pdf_icon  # Para mantener la referencia
    else:
        btn_pdf.config(text="PDF")
    btn_pdf.pack(side="left", padx=10)

# --------------------------------------------------
# Ventana para solicitar el nombre de la empresa y
# el año del balance (después del splash)
# --------------------------------------------------
def company_info_window(root, accounts_data):
    info_win = Toplevel(root)
    info_win.title("Información de la Empresa")
    info_win.geometry("400x200")
    info_win.configure(bg="#BDC3C7")
    
    # Centramos la ventana (opcional)
    screen_width = info_win.winfo_screenwidth()
    screen_height = info_win.winfo_screenheight()
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (200 // 2)
    info_win.geometry(f"400x200+{x}+{y}")
    
    tk.Label(info_win, text="Nombre de la Empresa:", bg="#BDC3C7", font=("Arial", 12)) \
        .pack(pady=10)
    entry_company = tk.Entry(info_win, width=40)
    entry_company.pack(pady=5)
    
    tk.Label(info_win, text="Año del Balance:", bg="#BDC3C7", font=("Arial", 12)) \
        .pack(pady=10)
    entry_year = tk.Entry(info_win, width=20)
    entry_year.pack(pady=5)
    
    def on_continue():
        company_name = entry_company.get().strip()
        year = entry_year.get().strip()
        if company_name == "" or year == "":
            messagebox.showerror("Error", "Por favor, ingrese todos los datos.")
        else:
            info_win.destroy()
            root.deiconify()
            main_window(root, accounts_data, company_name, year)
    
    btn_continue = tk.Button(info_win, text="Continuar", command=on_continue)
    btn_continue.pack(pady=20)
    
    info_win.grab_set()  # Modal

# --------------------
# Splash Screen
# --------------------
def splash_screen(root, accounts_data):
    splash = Toplevel()
    splash.title("Bienvenido")
    splash.geometry("400x200")
    splash.overrideredirect(True)
    splash.configure(bg="#2C3E50")
    
    # Centrar el splash
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (200 // 2)
    splash.geometry(f"400x200+{x}+{y}")
    
    lbl = tk.Label(splash, text="Sistema de Contabilidad\nB A L A N C E  G E N E R A L", 
                   font=("Arial", 16), bg="#2C3E50", fg="white")
    lbl.pack(expand=True, fill="both")
    
    def close_splash():
        splash.destroy()
        # Luego del splash se solicita la información de la empresa
        company_info_window(root, accounts_data)
    
    splash.after(3000, close_splash)

# --------------------
# Función para iniciar la app
# --------------------
def run_app():
    accounts_data = load_csv("balance2.csv")
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal hasta finalizar el splash y la info de empresa
    splash_screen(root, accounts_data)
    root.mainloop()

if __name__ == "__main__":
    run_app()