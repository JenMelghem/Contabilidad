import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox

class BalanceGeneralApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestión de Balance General con Depreciaciones")
        self.setGeometry(100, 100, 1000, 600)

        # Lista para almacenar las cuentas
        self.cuentas = []

        # Cargar cuentas desde el archivo CSV
        self.cargar_cuentas_desde_csv("catalogo.csv")

        # Crear widgets
        self.nombre_cuenta_input = QLineEdit(self)
        self.saldo_input = QLineEdit(self)
        self.tipo_activo_combo = QComboBox(self)
        self.tipo_activo_combo.addItems(["No es activo fijo", "Activo fijo"])
        self.vida_util_input = QLineEdit(self)
        self.vida_util_input.setPlaceholderText("Vida útil (años)")
        self.agregar_button = QPushButton("Agregar Cuenta", self)
        self.editar_button = QPushButton("Editar Cuenta", self)
        self.eliminar_button = QPushButton("Eliminar Cuenta", self)
        self.buscar_input = QLineEdit(self)
        self.buscar_button = QPushButton("Buscar", self)
        self.tabla_cuentas = QTableWidget(self)
        self.balance_label = QLabel("Balance General: $0.00", self)

        # Configurar la tabla
        self.tabla_cuentas.setColumnCount(5)
        self.tabla_cuentas.setHorizontalHeaderLabels(["Código", "Nombre", "Saldo", "Tipo", "Valor Depreciado"])

        # Diseño de la interfaz
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Nombre de la Cuenta:"))
        form_layout.addWidget(self.nombre_cuenta_input)
        form_layout.addWidget(QLabel("Saldo:"))
        form_layout.addWidget(self.saldo_input)
        form_layout.addWidget(QLabel("Tipo de Activo:"))
        form_layout.addWidget(self.tipo_activo_combo)
        form_layout.addWidget(QLabel("Vida Útil (años):"))
        form_layout.addWidget(self.vida_util_input)
        form_layout.addWidget(self.agregar_button)
        form_layout.addWidget(self.editar_button)
        form_layout.addWidget(self.eliminar_button)

        buscar_layout = QHBoxLayout()
        buscar_layout.addWidget(QLabel("Buscar por Código:"))
        buscar_layout.addWidget(self.buscar_input)
        buscar_layout.addWidget(self.buscar_button)

        layout.addLayout(form_layout)
        layout.addLayout(buscar_layout)
        layout.addWidget(self.tabla_cuentas)
        layout.addWidget(self.balance_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectar señales
        self.agregar_button.clicked.connect(self.agregar_cuenta)
        self.editar_button.clicked.connect(self.editar_cuenta)
        self.eliminar_button.clicked.connect(self.eliminar_cuenta)
        self.buscar_button.clicked.connect(self.buscar_cuenta)
        self.tabla_cuentas.itemSelectionChanged.connect(self.seleccionar_cuenta)

        # Actualizar la tabla y el balance al iniciar
        self.actualizar_tabla()
        self.calcular_balance()

    def cargar_cuentas_desde_csv(self, archivo_csv):
        try:
            with open(archivo_csv, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.cuentas.append({
                        "codigo": row['codigo'],
                        "nombre": row['nombre'],
                        "saldo": float(row['Saldo']),
                        "tipo": row.get('tipo', 'No es activo fijo'),
                        "vida_util": int(row.get('vida_util', 0)),
                        "depreciacion_acumulada": float(row.get('depreciacion_acumulada', 0.0))
                    })
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"El archivo {archivo_csv} no fue encontrado.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al leer el archivo CSV: {e}")

    def guardar_cuentas_en_csv(self, archivo_csv):
        try:
            with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["codigo", "nombre", "Saldo", "tipo", "vida_util", "depreciacion_acumulada"])
                writer.writeheader()
                for cuenta in self.cuentas:
                    writer.writerow({
                        "codigo": cuenta["codigo"],
                        "nombre": cuenta["nombre"],
                        "Saldo": cuenta["saldo"],
                        "tipo": cuenta["tipo"],
                        "vida_util": cuenta["vida_util"],
                        "depreciacion_acumulada": cuenta["depreciacion_acumulada"]
                    })
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar el archivo CSV: {e}")

    def agregar_cuenta(self):
        nombre = self.nombre_cuenta_input.text()
        saldo = self.saldo_input.text()
        tipo = self.tipo_activo_combo.currentText()
        vida_util = self.vida_util_input.text()

        if nombre and saldo:
            try:
                saldo = float(saldo)
                vida_util = int(vida_util) if vida_util else 0
                depreciacion_acumulada = 0.0

                if tipo == "Activo fijo" and vida_util > 0:
                    depreciacion_acumulada = saldo / vida_util  # Depreciación anual

                self.cuentas.append({
                    "codigo": nombre,  # Usar el nombre como código temporal
                    "nombre": nombre,
                    "saldo": saldo,
                    "tipo": tipo,
                    "vida_util": vida_util,
                    "depreciacion_acumulada": depreciacion_acumulada
                })
                self.actualizar_tabla()
                self.calcular_balance()
                self.guardar_cuentas_en_csv("catalogo_cuentas.csv")
                self.nombre_cuenta_input.clear()
                self.saldo_input.clear()
                self.vida_util_input.clear()
            except ValueError:
                QMessageBox.warning(self, "Error", "El saldo y la vida útil deben ser números válidos.")
        else:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")

    def editar_cuenta(self):
        selected_items = self.tabla_cuentas.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            nombre = self.nombre_cuenta_input.text()
            saldo = self.saldo_input.text()
            tipo = self.tipo_activo_combo.currentText()
            vida_util = self.vida_util_input.text()

            if nombre and saldo:
                try:
                    saldo = float(saldo)
                    vida_util = int(vida_util) if vida_util else 0
                    depreciacion_acumulada = 0.0

                    if tipo == "Activo fijo" and vida_util > 0:
                        depreciacion_acumulada = saldo / vida_util  # Depreciación anual

                    self.cuentas[row]["nombre"] = nombre
                    self.cuentas[row]["saldo"] = saldo
                    self.cuentas[row]["tipo"] = tipo
                    self.cuentas[row]["vida_util"] = vida_util
                    self.cuentas[row]["depreciacion_acumulada"] = depreciacion_acumulada

                    self.actualizar_tabla()
                    self.calcular_balance()
                    self.guardar_cuentas_en_csv("catalogo_cuentas.csv")
                    self.nombre_cuenta_input.clear()
                    self.saldo_input.clear()
                    self.vida_util_input.clear()
                except ValueError:
                    QMessageBox.warning(self, "Error", "El saldo y la vida útil deben ser números válidos.")
            else:
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta para editar.")

    def eliminar_cuenta(self):
        selected_items = self.tabla_cuentas.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            del self.cuentas[row]
            self.actualizar_tabla()
            self.calcular_balance()
            self.guardar_cuentas_en_csv("catalogo_cuentas.csv")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta para eliminar.")

    def buscar_cuenta(self):
        codigo_buscar = self.buscar_input.text()
        if codigo_buscar:
            for i, cuenta in enumerate(self.cuentas):
                if cuenta["codigo"] == codigo_buscar:
                    self.tabla_cuentas.selectRow(i)
                    self.tabla_cuentas.setFocus()
                    return
            QMessageBox.warning(self, "Error", "No se encontró ninguna cuenta con ese código.")
        else:
            QMessageBox.warning(self, "Error", "Ingresa un código para buscar.")

    def seleccionar_cuenta(self):
        selected_items = self.tabla_cuentas.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            cuenta = self.cuentas[row]
            self.nombre_cuenta_input.setText(cuenta["nombre"])
            self.saldo_input.setText(str(cuenta["saldo"]))
            self.tipo_activo_combo.setCurrentText(cuenta["tipo"])
            self.vida_util_input.setText(str(cuenta["vida_util"]))

    def actualizar_tabla(self):
        self.tabla_cuentas.setRowCount(len(self.cuentas))
        for i, cuenta in enumerate(self.cuentas):
            self.tabla_cuentas.setItem(i, 0, QTableWidgetItem(cuenta["codigo"]))
            self.tabla_cuentas.setItem(i, 1, QTableWidgetItem(cuenta["nombre"]))
            self.tabla_cuentas.setItem(i, 2, QTableWidgetItem(f"{cuenta['saldo']:.2f}"))
            self.tabla_cuentas.setItem(i, 3, QTableWidgetItem(cuenta["tipo"]))
            valor_depreciado = cuenta["saldo"] - cuenta["depreciacion_acumulada"]
            self.tabla_cuentas.setItem(i, 4, QTableWidgetItem(f"{valor_depreciado:.2f}"))

    def calcular_balance(self):
        total = sum(cuenta["saldo"] - cuenta["depreciacion_acumulada"] for cuenta in self.cuentas)
        self.balance_label.setText(f"Balance General: ${total:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BalanceGeneralApp()
    window.show()
    sys.exit(app.exec())