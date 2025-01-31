import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication
from ui import BalanceUI  

class BalanceApp(BalanceUI):
    def __init__(self):
        super().__init__()
        self.btnCargar.clicked.connect(self.cargar_csv)  

    def cargar_csv(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo CSV", "", "CSV Files (*.csv)")
        if archivo:
            df = pd.read_csv(archivo)
            self.mostrar_tabla(df)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BalanceApp()
    ventana.show()
    sys.exit(app.exec())
