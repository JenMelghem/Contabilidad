from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog,
                             QTableWidget, QTableWidgetItem, QLabel)

class BalanceUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Configura la interfaz gráfica."""
        self.setWindowTitle("Balance General")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout()
        
        # Botón para cargar CSV
        self.btnCargar = QPushButton("Cargar CSV")
        layout.addWidget(self.btnCargar)

        # Tabla para mostrar los datos
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)
        
        # Etiqueta para mensajes
        self.lblMensaje = QLabel("Carga un archivo CSV para visualizar los datos")
        layout.addWidget(self.lblMensaje)
        
        self.setLayout(layout)

    def mostrar_tabla(self, df):
        """Carga un DataFrame en la tabla."""
        self.tabla.setRowCount(df.shape[0])
        self.tabla.setColumnCount(df.shape[1])
        self.tabla.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
