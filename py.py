import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QFileDialog, QTableView, QMessageBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant


class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(PandasModel, self).__init__(parent)
        self._data = df.copy()

    def rowCount(self, parent=None):
        return len(self._data.index)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return QVariant()


class DragDropWidget(QWidget):
    def __init__(self, parent=None):
        super(DragDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.label = QLabel("Arraste e solte o arquivo CSV aqui ou clique no botão para selecionar.")
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.csv'):
                self.label.setText(f"Arquivo carregado: {file_path}")
                self.parent().process_file(file_path)
            else:
                QMessageBox.warning(self, "Arquivo inválido", "Por favor, arraste um arquivo CSV válido.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de CSV")
        self.resize(800, 600)
        
        self.df_processed = None
        
       
        self.drag_drop_widget = DragDropWidget(self)
        
        
        self.select_button = QPushButton("Selecionar arquivo CSV")
        self.select_button.clicked.connect(self.open_file_dialog)
        
        
        self.save_button = QPushButton("Salvar CSV Processado")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_file_dialog)
        
        
        self.table_view = QTableView()
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.drag_drop_widget)
        layout.addWidget(self.select_button)
        layout.addWidget(self.table_view)
        layout.addWidget(self.save_button)
        self.setCentralWidget(central_widget)
    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.drag_drop_widget.label.setText(f"Arquivo carregado: {file_path}")
            self.process_file(file_path)
    
    def process_file(self, file_path):
        try:
            df = pd.read_csv(file_path)
            if 'nome' not in df.columns:
                QMessageBox.warning(self, "Erro", "O arquivo CSV não possui a coluna 'nome'.")
                return
            
            df['nome'] = df['nome'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)
            self.df_processed = df
           
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.save_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar o arquivo: {e}")
    
    def save_file_dialog(self):
        if self.df_processed is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV Processado", "csv2.csv", "CSV Files (*.csv)")
            if file_path:
                try:
                    self.df_processed.to_csv(file_path, index=False)
                    QMessageBox.information(self, "Sucesso", "Arquivo CSV processado salvo com sucesso!")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao salvar o arquivo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

  
    # Esse código implementa uma aplicação gráfica em Python usando PyQt5 para processar arquivos CSV.
