from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QLabel)

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
