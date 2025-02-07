import sys
import csv
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from PyQt6.QtWidgets import QFileDialog
import openpyxl

class BalanceGeneral(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Balance General")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Campos de entrada
        self.label_codigo = QLabel("Código:")
        self.input_codigo = QLineEdit()
        self.input_codigo.textChanged.connect(self.actualizar_datos)  # Detectar cambios

        self.label_saldo = QLabel("Saldo:")
        self.input_saldo = QLineEdit()

        # Botón para agregar cuenta
        self.btn_agregar = QPushButton("Agregar Cuenta")
        self.btn_agregar.clicked.connect(self.agregar_cuenta)

        # Tabla para mostrar cuentas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre", " ", " ", " ", " "])

        # Botón para calcular balance
        self.btn_calcular = QPushButton("Calcular Balance General")
        self.btn_calcular.clicked.connect(self.calcular_balance)

        self.btn_exportar = QPushButton("Exportar a PDF")
        self.btn_exportar.clicked.connect(self.exportar_pdf)

        self.btn_exportar_excel = QPushButton("Exportar a Excel")
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)

        # Resultados del balance
        self.label_activos = QLabel("Total Activos: 0.00")
        self.label_pasivos = QLabel("Total Pasivos: 0.00")
        self.label_patrimonio = QLabel("Total Patrimonio: 0.00")
        self.label_mensaje = QLabel("")  # Para mensajes de error

        # Agregar widgets al layout
        layout.addWidget(self.label_codigo)
        layout.addWidget(self.input_codigo)
        layout.addWidget(self.label_saldo)
        layout.addWidget(self.input_saldo)
        layout.addWidget(self.btn_agregar)
        layout.addWidget(self.tabla)
        layout.addWidget(self.btn_exportar_excel)
        layout.addWidget(self.btn_calcular)
        layout.addWidget(self.btn_exportar)
        layout.addWidget(self.label_activos)
        layout.addWidget(self.label_pasivos)
        layout.addWidget(self.label_patrimonio)
        layout.addWidget(self.label_mensaje)
        self.setLayout(layout)

        # Cargar datos desde CSV
        self.cuentas_csv = self.cargar_csv("balance.csv")
        self.llenar_tabla()

    def cargar_csv(self, archivo):
        """Carga los datos del CSV en un diccionario."""
        datos = {}
        try:
            with open(archivo, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Omitir encabezado
                for row in reader:
                    if len(row) >= 2:
                        codigo, nombre = row[:2]
                        datos[codigo] = nombre  # Guardar código -> nombre
        except FileNotFoundError:
            print(f"⚠️ No se encontró el archivo {archivo}")
        return datos
    
    def llenar_tabla(self):
        """Llena la tabla con los datos del CSV y deja los valores adicionales con un punto."""
        for codigo, nombre in self.cuentas_csv.items():
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(codigo))
            self.tabla.setItem(row, 1, QTableWidgetItem(nombre))

            # Si el código es uno de los especiales, solo poner nombre y código, pero sin saldo
            if codigo in ["1", "1.1", "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.4.1", "1.1.4.2", "1.1.5", "1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", 
                        "2", "2.1", "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.2", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "3", "3.1", "3.1.2", "3.2", "3.2.2", "3.2.3"]:
                self.tabla.setItem(row, 2, QTableWidgetItem(""))  # Columna x vacía
                self.tabla.setItem(row, 3, QTableWidgetItem(""))  # Columna y vacía
                self.tabla.setItem(row, 4, QTableWidgetItem(""))  # Columna z vacía
                self.tabla.setItem(row, 5, QTableWidgetItem(""))  # Saldo vacío
            else:
                # De lo contrario, asigna un punto (".") a las columnas x, y, z y 0 en el saldo
                self.tabla.setItem(row, 2, QTableWidgetItem("0.00"))  # Columna x
                self.tabla.setItem(row, 3, QTableWidgetItem("0.00"))  # Columna y
                self.tabla.setItem(row, 4, QTableWidgetItem("0.00"))  # Columna z
                self.tabla.setItem(row, 5, QTableWidgetItem("0.00"))  # Saldo inicial en 0

        

    def actualizar_datos(self):
        """Resalta la fila correspondiente al código ingresado."""
        codigo = self.input_codigo.text()
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 0).text() == codigo:
                self.tabla.selectRow(row)
                break

    def agregar_cuenta(self):
        """Agrega saldo solo si el código no es 1, 2 o 3 y cuentas que no deben llevar un saldo"""
        codigo = self.input_codigo.text()
        saldo = self.input_saldo.text()

        if codigo in ["1", "1.1", "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.4.1", "1.1.4.2", "1.1.5", "1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", 
                    "2", "2.1", "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.2", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "3", "3.1", "3.1.2", "3.2", "3.2.2", "3.2.3"]:
            self.label_mensaje.setText(f"⚠️ No se puede agregar saldo al código {codigo}.")
            return

        if codigo and saldo:
            try:
                saldo = float(saldo)
                for row in range(self.tabla.rowCount()):
                    if self.tabla.item(row, 0).text() == codigo:
                        self.sumar_saldos_subgrupos_y_actualizar()
                        self.sumar_saldos_grupos_y_actualizar()
                        self.sumar_saldos_clases_y_actualizar()
                        #CALCULO DE LOS SALDOS NETOS DE LAS CUENTAS
                        #Despues de agragar cada depreciacion se debe calcular el saldo neto de su repectiva cuenta
                        if codigo in ["1.2.2.2.1", "1.2.2.3.1", "1.2.2.4.1", "1.2.2.5.1", "1.2.2.6.1", "1.2.2.7.1", "1.2.2.8.1"]:
                            self.tabla.setItem(row, 2, QTableWidgetItem(str(saldo)))  # Columna x
                            
                            # Realizar la operación matemática y actualizar la columna y
                            if codigo == "1.2.2.2.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.2":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            
                            if  codigo == "1.2.2.3.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.3":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            if  codigo == "1.2.2.4.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.4":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            if  codigo == "1.2.2.5.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.5":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            if  codigo == "1.2.2.6.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.6":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            if  codigo == "1.2.2.7.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.7":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                            if  codigo == "1.2.2.8.1":
                                for r in range(self.tabla.rowCount()):
                                    if self.tabla.item(r, 0).text() == "1.2.2.8":
                                        y_valor = float(self.tabla.item(r, 3).text())
                                        self.tabla.setItem(r, 2, QTableWidgetItem(str(y_valor)))  # Mover valor de y a x
                                        self.tabla.setItem(r, 3, QTableWidgetItem("0"))  # Dejar y en 0
                                        self.tabla.setItem(r, 4, QTableWidgetItem("0"))  # Dejar z en 0
                                        
                                        x_valor = float(self.tabla.item(r, 2).text())
                                        resultado = x_valor - saldo
                                        self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado)))  # Columna y
                                        self.sumar_saldos_subgrupos_y_actualizar()
                                        self.sumar_saldos_grupos_y_actualizar()
                                        self.sumar_saldos_clases_y_actualizar()
                                        break
                           
                            #CALCULO DE LOS SALDOS NETOS DE LOS SUBGRUPOS
                            #Si hubo calculo de saldo neto por la existencia de depreciaciones el calculo de los subgrupos es de la siguiente forma
                            self.sumar_saldos_subgrupos_y_actualizar()
                            #CALCULO DE LOS SALDOS DE LOS GRUPOS
                            #Si hubo calculo de saldo neto por la existencia de depreciaciones el calculo de los grupos es de la siguiente forma
                            self.sumar_saldos_grupos_y_actualizar()
                            #CALCULO DE LOS SALDOS DE LAS CLASES
                            #Si hubo calculo de saldo neto por la existencia de depreciaciones el calculo de las clases es de la siguiente forma
                            self.sumar_saldos_clases_y_actualizar()
                        
                        else:
                            self.tabla.setItem(row, 3, QTableWidgetItem(str(saldo)))  # Columna y
                            self.sumar_saldos_subgrupos_y_actualizar()
                            self.sumar_saldos_grupos_y_actualizar()
                            self.sumar_saldos_clases_y_actualizar()
                            self.label_mensaje.setText("")  # Limpiar mensaje de error
                        break
                self.input_codigo.clear()
                self.input_saldo.clear()
            except ValueError:
                self.label_mensaje.setText("⚠️ Saldo debe ser un número válido.")
        else:
            self.label_mensaje.setText("⚠️ Completa todos los campos.")
    
        
            
    def sumar_saldos_clases_y_actualizar(self):
        # Inicializar la suma
        suma_saldos1 = 0.0
        suma_saldos2 = 0.0
        suma_saldos3 = 0.0
        
        # Lista de códigos a sumar
        codigos_a_sumar1 = ["1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5", "1.1.2.1", "1.1.2.2", "1.1.3.1", "1.1.3.2", "1.1.3.3", "1.1.3.4", "1.1.3.5", "1.1.3.6", "1.1.3.7", "1.1.3.8", "1.1.3.9",
        "1.1.4.1.1", "1.1.4.1.2", "1.1.4.2.1", "1.1.4.2.2", "1.1.4.2.3", "1.1.5.1", "1.1.5.2", "1.1.5.3", "1.1.5.4", "1.1.5.5", "1.1.5.6", "1.1.5.7", "1.1.5.8", "1.1.5.9"
        , "1.2.1.1", "1.2.1.2", "1.2.1.3", "1.2.1.4", "1.2.2.1", "1.2.2.2", "1.2.2.2.1", "1.2.2.3", "1.2.2.3.1", "1.2.2.4", "1.2.2.4.1", "1.2.2.5", "1.2.2.5.1", "1.2.2.6", "1.2.2.6.1", 
        "1.2.2.7", "1.2.2.7.1", "1.2.2.8", "1.2.2.8.1", "1.2.3.1", "1.2.3.2", "1.2.3.3", "1.2.3.4", "1.2.4.1", "1.2.4.2", "1.2.5.1", "1.2.5.2", "1.2.5.3"]
        codigos_a_sumar2 = ["2.1.1.1", "2.1.1.2", "2.1.1.3", "2.1.1.4", "2.1.1.5", "2.1.1.6", "2.1.2.1", "2.1.2.2", "2.1.3.1", "2.1.3.2", "2.1.3.3", "2.1.4.1", "2.1.4.2", "2.1.4.3", "2.1.4.4", "2.1.4.5" 
        , "2.2.1.1", "2.2.1.2", "2.2.2.1", "2.2.2.2","2.2.3.1", "2.2.3.2", "2.2.3.3","2.2.4.1", "2.2.4.2", "2.2.4.3"]
        codigos_a_sumar3 = ["2.1.1.1", "2.1.1.2", "2.1.1.3", "2.1.1.4", "2.1.1.5", "2.1.1.6", "2.1.2.1", "2.1.2.2", "2.1.3.1", "2.1.3.2", "2.1.3.3", "2.1.4.1", "2.1.4.2", "2.1.4.3", "2.1.4.4", "2.1.4.5" 
        , "2.2.1.1", "2.2.1.2", "2.2.2.1", "2.2.2.2","2.2.3.1", "2.2.3.2", "2.2.3.3","2.2.4.1", "2.2.4.2", "2.2.4.3", "3.1.1", "3.1.2.1", "3.1.2.2", "3.2.1", "3.2.2.1", "3.2.2.2", "3.2.2.3", "3.2.3.1", "3.2.3.2"]
        codigo_total_Activo = "010"
        codigo_total_Pasivo = "020"
        codigo_total_Pasivo_Mas_Patrimonio = "010020"
        
       # Iterar sobre las filas de la tabla para las cuentas de la clase Activo
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo in codigos_a_sumar1:
                y_valor = float(self.tabla.item(row, 5).text())
                if y_valor > 0:
                    suma_saldos1 += y_valor
                    
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 0).text() == codigo_total_Activo:
                self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos1)))
                break
            
        # Iterar sobre las filas de la tabla para las cuentas de la clase Pasivo
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo in codigos_a_sumar2:
                y_valor = float(self.tabla.item(row, 5).text())
                if y_valor > 0:
                    suma_saldos2 += y_valor
                    
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 0).text() == codigo_total_Pasivo:
                self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos2)))
                break
            
        # Iterar sobre las filas de la tabla para las cuentas de Pasivo y Patrimonio
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo in codigos_a_sumar3:
                y_valor = float(self.tabla.item(row, 5).text())
                if y_valor > 0:
                    suma_saldos3 += y_valor
                    
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 0).text() == codigo_total_Pasivo_Mas_Patrimonio:
                self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos3)))
                break
        
    def sumar_saldos_grupos_y_actualizar(self):
        # Inicializar la suma
        suma_saldos1 = 0.0
        ultimo_codigo1 = None
        suma_saldos2 = 0.0
        ultimo_codigo2 = None
        suma_saldos3 = 0.0
        ultimo_codigo3 = None
        suma_saldos4 = 0.0
        ultimo_codigo4 = None
        suma_saldos5 = 0.0
        ultimo_codigo5 = None

        # Lista de códigos a sumar
        codigos_a_sumar1 = ["1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5", "1.1.2.1", "1.1.2.2", "1.1.3.1", "1.1.3.2", "1.1.3.3", "1.1.3.4", "1.1.3.5", "1.1.3.6", "1.1.3.7", "1.1.3.8", "1.1.3.9",
        "1.1.4.1.1", "1.1.4.1.2", "1.1.4.2.1", "1.1.4.2.2", "1.1.4.2.3", "1.1.5.1", "1.1.5.2", "1.1.5.3", "1.1.5.4", "1.1.5.5", "1.1.5.6", "1.1.5.7", "1.1.5.8", "1.1.5.9"]
        codigos_a_sumar2 = ["1.2.1.1", "1.2.1.2", "1.2.1.3", "1.2.1.4", "1.2.2.1", "1.2.2.2", "1.2.2.2.1", "1.2.2.3", "1.2.2.3.1", "1.2.2.4", "1.2.2.4.1", "1.2.2.5", "1.2.2.5.1", "1.2.2.6", "1.2.2.6.1", 
        "1.2.2.7", "1.2.2.7.1", "1.2.2.8", "1.2.2.8.1", "1.2.3.1", "1.2.3.2", "1.2.3.3", "1.2.3.4", "1.2.4.1", "1.2.4.2", "1.2.5.1", "1.2.5.2", "1.2.5.3"]
        codigos_a_sumar3 = ["2.1.1.1", "2.1.1.2", "2.1.1.3", "2.1.1.4", "2.1.1.5", "2.1.1.6", "2.1.2.1", "2.1.2.2", "2.1.3.1", "2.1.3.2", "2.1.3.3", "2.1.4.1", "2.1.4.2", "2.1.4.3", "2.1.4.4", "2.1.4.5"] 
        codigos_a_sumar4 = ["2.2.1.1", "2.2.1.2", "2.2.2.1", "2.2.2.2","2.2.3.1", "2.2.3.2", "2.2.3.3","2.2.4.1", "2.2.4.2", "2.2.4.3"]
        codigos_a_sumar5 = ["3.1.1", "3.1.2.1", "3.1.2.2", "3.2.1", "3.2.2.1", "3.2.2.2", "3.2.2.3", "3.2.3.1", "3.2.3.2"]
        
        # Iterar sobre las filas de la tabla para las cuentas del grupo Activo Corriente
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo in codigos_a_sumar1:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos1 += y_valor
                    self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos1)))  #Columna Saldo
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo1:
                            self.tabla.setItem(row, 5, QTableWidgetItem("0"))  # Dejar Saldo en 0
                      
                    ultimo_codigo1 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo1:
                            self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos1)))  #Columna Saldo
                            break
            
             # Iterar sobre las filas de la tabla para las cuentas del grupo Activo No Corriente           
            if codigo in codigos_a_sumar2:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos2 += y_valor
                    self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos2)))  #Columna Saldo
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo2:
                            self.tabla.setItem(row, 5, QTableWidgetItem("0"))  # Dejar Saldo en 0
                      
                    ultimo_codigo2 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo2:
                            self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos2)))  #Columna Saldo
                            break
            
            # Iterar sobre las filas de la tabla para las cuentas del grupo Pasivo Corriente          
            if codigo in codigos_a_sumar3:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos3 += y_valor
                    self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos3)))  #Columna Saldo
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo3:
                            self.tabla.setItem(row, 5, QTableWidgetItem("0"))  # Dejar Saldo en 0
                      
                    ultimo_codigo3 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo3:
                            self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos3)))  #Columna Saldo
                            break

            # Iterar sobre las filas de la tabla para las cuentas del grupo Pasivo No Corriente          
            if codigo in codigos_a_sumar4:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos4 += y_valor
                    self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos4)))  #Columna Saldo
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4:
                            self.tabla.setItem(row, 5, QTableWidgetItem("0"))  # Dejar Saldo en 0
                      
                    ultimo_codigo4 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4:
                            self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos4)))  #Columna Saldo
                            break 
            
            # Iterar sobre las filas de la tabla para las cuentas del Patrimonio          
            if codigo in codigos_a_sumar5:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos5 += y_valor
                    self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos5)))  #Columna Saldo
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo5:
                            self.tabla.setItem(row, 5, QTableWidgetItem("0"))  # Dejar Saldo en 0
                      
                    ultimo_codigo5 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo5:
                            self.tabla.setItem(row, 5, QTableWidgetItem(str(suma_saldos5)))  #Columna Saldo
                            break

     
    def sumar_saldos_subgrupos_y_actualizar(self):
        # Inicializar la suma
        suma_saldos1 = 0.0
        ultimo_codigo1 = None
        suma_saldos2 = 0.0
        ultimo_codigo2 = None
        suma_saldos3 = 0.0
        ultimo_codigo3 = None
        suma_saldos4_1 = 0.0
        ultimo_codigo4_1 = None
        suma_saldos4_2 = 0.0
        ultimo_codigo4_2 = None
        suma_saldos5 = 0.0
        ultimo_codigo5 = None
        suma_saldos6 = 0.0
        ultimo_codigo6 = None
        suma_saldos7 = 0.0
        ultimo_codigo7 = None
        suma_saldos8 = 0.0
        ultimo_codigo8 = None
        suma_saldos9 = 0.0
        ultimo_codigo9 = None
        suma_saldos10 = 0.0
        ultimo_codigo10 = None
        suma_saldos11 = 0.0
        ultimo_codigo11 = None
        suma_saldos12 = 0.0
        ultimo_codigo12 = None
        suma_saldos13 = 0.0
        ultimo_codigo13 = None
        suma_saldos14 = 0.0
        ultimo_codigo14 = None
        suma_saldos15 = 0.0
        ultimo_codigo15 = None
        suma_saldos16 = 0.0
        ultimo_codigo16 = None
        suma_saldos17 = 0.0
        ultimo_codigo17 = None
        suma_saldos18 = 0.0
        ultimo_codigo18 = None
        suma_saldos19 = 0.0
        ultimo_codigo19 = None
        suma_saldos20 = 0.0
        ultimo_codigo20 = None
        suma_saldos21 = 0.0
        ultimo_codigo21 = None

        # Lista de códigos a sumar
        codigos_a_sumar1 = ["1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5"]
        codigos_a_sumar2 = ["1.1.2.1", "1.1.2.2"]
        codigos_a_sumar3 = ["1.1.3.1", "1.1.3.2", "1.1.3.3", "1.1.3.4", "1.1.3.5", "1.1.3.6", "1.1.3.7", "1.1.3.8", "1.1.3.9"]
        codigos_a_sumar4_1 = ["1.1.4.1.1", "1.1.4.1.2"]
        codigos_a_sumar4_2 = ["1.1.4.2.1", "1.1.4.2.2", "1.1.4.2.3"]
        codigos_a_sumar5 = ["1.1.5.1", "1.1.5.2", "1.1.5.3", "1.1.5.4", "1.1.5.5", "1.1.5.6", "1.1.5.7", "1.1.5.8", "1.1.5.9"]
        codigos_a_sumar6 = ["1.2.1.1", "1.2.1.2", "1.2.1.3", "1.2.1.4"]
        #CODIFICAR DETALLADAMENTE POR LA EXISTENCIA DE DEPRECIACIONES
        codigos_a_sumar7 = ["1.2.2.1", "1.2.2.2", "1.2.2.2.1", "1.2.2.3", "1.2.2.3.1", "1.2.2.4", "1.2.2.4.1", "1.2.2.5", "1.2.2.5.1", "1.2.2.6", "1.2.2.6.1", "1.2.2.7", "1.2.2.7.1", "1.2.2.8", "1.2.2.8.1"]
        #codigos_a_sumar7 = ["1.2.2.1", "1.2.2.2", "1.2.2.3", "1.2.2.4", "1.2.2.5", "1.2.2.6", "1.2.2.7", "1.2.2.8"]
        codigos_a_sumar8 = ["1.2.3.1", "1.2.3.2", "1.2.3.3", "1.2.3.4"]
        codigos_a_sumar9 = ["1.2.4.1", "1.2.4.2"]
        codigos_a_sumar10 = ["1.2.5.1", "1.2.5.2", "1.2.5.3"]
        codigos_a_sumar11 = ["2.1.1.1", "2.1.1.2", "2.1.1.3", "2.1.1.4", "2.1.1.5", "2.1.1.6"]
        codigos_a_sumar12 = ["2.1.2.1", "2.1.2.2"]
        codigos_a_sumar13 = ["2.1.3.1", "2.1.3.2", "2.1.3.3"]
        codigos_a_sumar14 = ["2.1.4.1", "2.1.4.2", "2.1.4.3", "2.1.4.4", "2.1.4.5"]
        codigos_a_sumar15 = ["2.2.1.1", "2.2.1.2"]
        codigos_a_sumar16 = ["2.2.2.1", "2.2.2.2"]
        codigos_a_sumar17 = ["2.2.3.1", "2.2.3.2", "2.2.3.3"]
        codigos_a_sumar18 = ["2.2.4.1", "2.2.4.2", "2.2.4.3"]
        codigos_a_sumar19 = ["3.1.2.1", "3.1.2.2"]
        codigos_a_sumar20 = ["3.2.2.1", "3.2.2.2", "3.2.2.3"]
        codigos_a_sumar21 = ["3.2.3.1", "3.2.3.2"]
        
        # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.1
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo in codigos_a_sumar1:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos1 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos1)))  #Columna Z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo1:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo1 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo1:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos1)))  # Columna z
                            break
            
             # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.2           
            if codigo in codigos_a_sumar2:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos2 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos2)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo2:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo2 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo2:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos2)))  # Columna z
                            break
            
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.3           
            if codigo in codigos_a_sumar3:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos3 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos3)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo3:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo3 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo3:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos3)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.4.1           
            if codigo in codigos_a_sumar4_1:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos4_1 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos4_1)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4_1:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo4_1 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4_1:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos4_1)))  # Columna z
                            break 
            
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.4.2           
            if codigo in codigos_a_sumar4_2:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos4_2 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos4_2)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4_2:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo4_2 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo4_2:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos4_2)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.1.5          
            if codigo in codigos_a_sumar5:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos5 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos5)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo5:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo5 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo5:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos5)))  # Columna z
                            break
                        
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.2.1         
            if codigo in codigos_a_sumar6:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos6 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos6)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo6:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo6 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo6:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos6)))  # Columna z
                            break
                        
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.2.2  
            #CODIFICAR DETALLADAMENTE POR LA EXISTENCIA DE DEPRECIACIONES              
            if codigo in codigos_a_sumar7:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos7 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos7)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo7:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo7 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo7:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos7)))  # Columna z
                            break   

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.2.3         
            if codigo in codigos_a_sumar8:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos8 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos8)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo8:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo8 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo8:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos8)))  # Columna z
                            break   
                            
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.2.4         
            if codigo in codigos_a_sumar9:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos9 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos9)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo9:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo9 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo9:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos9)))  # Columna z
                            break
                
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 1.2.5         
            if codigo in codigos_a_sumar10:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos10 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos10)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo10:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo10 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo10:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos10)))  # Columna z
                            break
                
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.1.1         
            if codigo in codigos_a_sumar11:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos11 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos11)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo11:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo11 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo11:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos11)))  # Columna z
                            break
     
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.1.2         
            if codigo in codigos_a_sumar12:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos12 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos12)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo12:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo12 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo12:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos12)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.1.3        
            if codigo in codigos_a_sumar13:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos13 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos13)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo13:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo13 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo13:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos13)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.1.4        
            if codigo in codigos_a_sumar14:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos14 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos14)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo14:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo14 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo14:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos14)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.2.1       
            if codigo in codigos_a_sumar15:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos15 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos15)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo15:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo15 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo15:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos15)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.2.2       
            if codigo in codigos_a_sumar16:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos16 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos16)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo16:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo16 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo16:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos16)))  # Columna z
                            break
                        
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.2.3       
            if codigo in codigos_a_sumar17:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos17 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos17)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo17:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo17 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo17:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos17)))  # Columna z
                            break  
                              
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 2.2.4      
            if codigo in codigos_a_sumar18:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos18 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos18)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo18:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo18 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo18:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos18)))  # Columna z
                            break
            
            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 3.1.2      
            if codigo in codigos_a_sumar19:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos19 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos19)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo19:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo19 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo19:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos19)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 3.2.2      
            if codigo in codigos_a_sumar20:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos20 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos20)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo20:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo20 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo20:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos20)))  # Columna z
                            break

            # Iterar sobre las filas de la tabla para las cuentas del subgrupo 3.2.3    
            if codigo in codigos_a_sumar21:
                y_valor = float(self.tabla.item(row, 3).text())
                if y_valor > 0:
                    suma_saldos21 += y_valor
                    self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos21)))  # Columna z
                    
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo21:
                            self.tabla.setItem(row, 4, QTableWidgetItem("0"))  # Dejar y en 0
                      
                    ultimo_codigo21 = codigo  # Guardar el último código
                    for row in range(self.tabla.rowCount()):
                        if self.tabla.item(row, 0).text() == ultimo_codigo21:
                            self.tabla.setItem(row, 4, QTableWidgetItem(str(suma_saldos21)))  # Columna z
                            break

    def calcular_balance(self):
        """Calcula el total de activos, pasivos y patrimonio y elimina filas con saldo 0."""
        total_activos = 0
        total_pasivos = 0
        total_patrimonio = 0

        row = 0
        while row < self.tabla.rowCount():
            saldo_text = self.tabla.item(row, 5).text()
            x_text = self.tabla.item(row, 2).text()
            y_text = self.tabla.item(row, 3).text()
            z_text = self.tabla.item(row, 4).text()

            # Verificar si los valores son numéricos
            if (saldo_text and saldo_text.replace(".", "", 1).isdigit() and
                x_text and x_text.replace(".", "", 1).isdigit() and
                y_text and y_text.replace(".", "", 1).isdigit() and
                z_text and z_text.replace(".", "", 1).isdigit()):
                
                saldo = float(saldo_text)
                x = float(x_text)
                y = float(y_text)
                z = float(z_text)
                
                if saldo == 0 and x == 0 and y == 0 and z == 0:
                    self.tabla.removeRow(row)
                else:
                    if saldo == 0:
                        self.tabla.setItem(row, 5, QTableWidgetItem(""))  # Borrar saldo
                    if x == 0:
                        self.tabla.setItem(row, 2, QTableWidgetItem(""))  # Borrar x
                    if y == 0:
                        self.tabla.setItem(row, 3, QTableWidgetItem(""))  # Borrar y
                    if z == 0:
                        self.tabla.setItem(row, 4, QTableWidgetItem(""))  # Borrar z
                    row += 1
            else:
                # Si no es numérico, omitir esta fila
                row += 1

        # Eliminar filas de clases padre sin clases hijas con valor >0
        codigos_padre = ["1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "3.1.2", "3.2.2", "3.2.3"]
        for codigo_padre in codigos_padre:
            eliminar_padre = True
            for row in range(self.tabla.rowCount()):
                codigo = self.tabla.item(row, 0).text()
                if codigo.startswith(codigo_padre + "."):
                    saldo_text = self.tabla.item(row, 5).text()
                    x_text = self.tabla.item(row, 2).text()
                    y_text = self.tabla.item(row, 3).text()
                    z_text = self.tabla.item(row, 4).text()
                    if (saldo_text and saldo_text.replace(".", "", 1).isdigit() and float(saldo_text) > 0 or
                        x_text and x_text.replace(".", "", 1).isdigit() and float(x_text) > 0 or
                        y_text and y_text.replace(".", "", 1).isdigit() and float(y_text) > 0 or
                        z_text and z_text.replace(".", "", 1).isdigit() and float(z_text) > 0):
                        eliminar_padre = False
                        break
            if eliminar_padre:
                for row in range(self.tabla.rowCount()):
                    if self.tabla.item(row, 0).text() == codigo_padre:
                        self.tabla.removeRow(row)
                        break

        # Eliminar filas de clases abuelas sin clases padre con valor >0
        codigos_abuela = ["1", "1.1", "1.1.4.1", "1.1.4.2", "1.2", "2", "2.1", "2.2", "3", "3.1", "3.2"]
        for codigo_abuela in codigos_abuela:
            eliminar_abuela = True
            for row in range(self.tabla.rowCount()):
                codigo = self.tabla.item(row, 0).text()
                if codigo.startswith(codigo_abuela + "."):
                    saldo_text = self.tabla.item(row, 5).text()
                    x_text = self.tabla.item(row, 2).text()
                    y_text = self.tabla.item(row, 3).text()
                    z_text = self.tabla.item(row, 4).text()
                    if (saldo_text and saldo_text.replace(".", "", 1).isdigit() and float(saldo_text) > 0 or
                        x_text and x_text.replace(".", "", 1).isdigit() and float(x_text) > 0 or
                        y_text and y_text.replace(".", "", 1).isdigit() and float(y_text) > 0 or
                        z_text and z_text.replace(".", "", 1).isdigit() and float(z_text) > 0):
                        eliminar_abuela = False
                        break
            if eliminar_abuela:
                for row in range(self.tabla.rowCount()):
                    if self.tabla.item(row, 0).text() == codigo_abuela:
                        self.tabla.removeRow(row)
                        break
    
    # Obtener totales de activos y pasivos directamente de las filas correspondientes
        total_activos = 0
        total_pasivos = 0
        total_pasivo_mas_patrimonio = 0
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.item(row, 0).text()
            if codigo == "010":
                total_activos = float(self.tabla.item(row, 5).text())
            elif codigo == "020":
                total_pasivos = float(self.tabla.item(row, 5).text())
            elif codigo == "010020":
                total_pasivo_mas_patrimonio = float(self.tabla.item(row, 5).text())

        # Calcular el total de patrimonio
        total_patrimonio = total_pasivo_mas_patrimonio - total_pasivos

        # Actualizar etiquetas de totales
        self.label_activos.setText(f"Total Activos: {total_activos}")
        self.label_pasivos.setText(f"Total Pasivos: {total_pasivos}")
        self.label_patrimonio.setText(f"Total Patrimonio: {total_patrimonio}")
    
    def exportar_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "balance_general.pdf", "Archivos PDF (*.pdf)")

        if file_name:
            doc = SimpleDocTemplate(file_name, pagesize=letter)

            data = [[" ", " ", " ", " ", " ", " "]]
            for row in range(self.tabla.rowCount()):
                codigo = self.tabla.item(row, 0).text()
                nombre = self.tabla.item(row, 1).text()
                x = self.tabla.item(row, 2).text()
                y = self.tabla.item(row, 3).text()
                z = self.tabla.item(row, 4).text()
                saldo = self.tabla.item(row, 5).text()
                data.append([codigo, nombre, x, y, z, saldo])

            table = Table(data, colWidths=[80, 200, 60, 60, 60, 80])  # Más espacio para "Nombre"

            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Encabezado con fondo gris
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),  # Solo línea bajo el encabezado
            ]))

            doc.build([table])
            print(f"PDF guardado en {file_name}")

    def exportar_excel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "balance_general.xlsx", "Archivos Excel (*.xlsx)")

        if file_name:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append([" ", " ", " ", " ", " ", " "])

            for row in range(self.tabla.rowCount()):
                sheet.append([self.tabla.item(row, col).text() for col in range(6)])

            workbook.save(file_name)
            print(f"Excel guardado en {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BalanceGeneral()
    ventana.show()
    sys.exit(app.exec())
