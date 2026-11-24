from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QListWidget, QListWidgetItem, QStyle, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon
import re




class frontend(QWidget):
    senal_buscar_por_nombre = pyqtSignal(str)  #  str: texto buscado
    senal_pendrive_seleccionado = pyqtSignal(str)
    senal_vaciar = pyqtSignal()
    senal_matrices_seleccionadas = pyqtSignal(list) # lista de nombres de matrices seleccionadas
 


    def __init__(self):
        super().__init__()
        self.init_gui()

    def init_gui(self):
        self.setGeometry(600, 250, 600, 650)
        self.setWindowTitle('programa matrices')

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2d30;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #1e1f22;
                border: 1px solid #43454a;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #3574f0;
            }
            QListWidget {
                background-color: #1e1f22;
                border: 1px solid #43454a;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #393b40;
                border: 1px solid #4e5157;
                border-radius: 5px;
                padding: 6px 12px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #43454a;
            }
            QPushButton:pressed {
                background-color: #2b2d30;
            }
            QComboBox {
                background-color: #393b40;
                border: 1px solid #4e5157;
                border-radius: 5px;
                padding: 5px 10px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(self)

        self.buscador = QLineEdit(self)
        self.buscador.setPlaceholderText("Buscar matriz por nombre")
        self.buscador.setStyleSheet("padding: 8px; font-size: 14px;")
        self.buscador.textChanged.connect(self.filtrar_imagenes)
        layout.addWidget(self.buscador)

        self.lista_imagenes = QListWidget()
        self.lista_imagenes.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_imagenes.setResizeMode(QListWidget.ResizeMode.Adjust) # Se adapta al ancho
        self.lista_imagenes.setIconSize(QSize(100, 100)) # Tamaño de la imagen
        self.lista_imagenes.setGridSize(QSize(130, 140)) # Espacio total por celda
        self.lista_imagenes.setSpacing(10)
        self.lista_imagenes.setMovement(QListWidget.Movement.Static) # Evita que el usuario las desordene arrastrando

        self.lista_imagenes.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        self.lista_imagenes.setStyleSheet("""
            QListWidget::item {
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #CCE8FF;
                border: 2px solid #0078D7;
                color: black;
            }
        """)
        
        layoutH = QHBoxLayout()

        self.boton_añadir = QPushButton("añadir", self)
        self.boton_añadir.pressed.connect(self.agregar_elementos_seleccionados) 
        layoutH.addWidget(self.boton_añadir)

        self.boton_limpiar = QPushButton("limpiar pendrive", self)
        self.boton_limpiar.pressed.connect(self.senal_vaciar.emit)
        layoutH.addWidget(self.boton_limpiar)

        self.box_pendrives = QComboBox(self)
        self.box_pendrives.currentTextChanged.connect(self.senal_pendrive_seleccionado.emit)
        layoutH.addWidget(self.box_pendrives)

        layout.addLayout(layoutH)
        
        layout.addWidget(self.lista_imagenes)

        layoutH2 = QHBoxLayout()

        self.titulo_lista_seleccionados = QLabel("Matrices Seleccionadas", self)
        self.titulo_lista_seleccionados.setStyleSheet("padding: 8px; font-size: 16px;")
        layoutH2.addWidget(self.titulo_lista_seleccionados)
        layoutH2.addStretch(1)

        self.titulo_eliminar = QLabel("Para eliminar matrices, hacer doble click", self)
        self.titulo_eliminar.setStyleSheet("padding: 8px; font-size: 14px")
        layoutH2.addWidget(self.titulo_eliminar)
        layoutH2.addStretch(1)

        self.boton_anadir_al_pendrive = QPushButton("añadir matrices al pendrive", self)
        self.boton_anadir_al_pendrive.clicked.connect(self.accion_anadir_matrices_pendrive)
        layoutH2.addWidget(self.boton_anadir_al_pendrive)
        
        layoutH2.addStretch(10)
        layout.addLayout(layoutH2)

        self.lista_seleccionados = QListWidget()
        self.lista_seleccionados.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_seleccionados.setResizeMode(QListWidget.ResizeMode.Adjust) # Se adapta al ancho
        self.lista_seleccionados.setIconSize(QSize(100, 100)) # Tamaño de la imagen
        self.lista_seleccionados.setGridSize(QSize(130, 140)) # Espacio total por celda
        self.lista_seleccionados.setSpacing(10)
        self.lista_seleccionados.setMovement(QListWidget.Movement.Static) # Evita que el usuario las desordene arrastrando

        self.lista_seleccionados.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        self.lista_seleccionados.setStyleSheet("""
            QListWidget::item {
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #CCE8FF;
                border: 2px solid #0078D7;
                color: black;
            }
        """)

        self.lista_seleccionados.itemDoubleClicked.connect(self.eliminar_seleccionada)
        layout.addWidget(self.lista_seleccionados)

        self.show()

    def mostrar_error_ventana_pendrive(self):
        QMessageBox.critical(
            self, 
            "Error de pendrive", 
            "No se encontro un pendrive conectado para guardar las matrices."
        )
    
    def cargar_datos(self, lista):
        # Aquí pondrías tus rutas reales, ej: [("Gato", "ruta/gato.png"), ...]
        # Uso íconos nativos de Qt para que el ejemplo funcione de inmediato
        for dic in lista:
            item = QListWidgetItem(QIcon(dic["imagen"]), dic["nombre"])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, f"{dic["nombre"]}")
            self.lista_imagenes.addItem(item)
            print(f"item cargado {dic["nombre"]}")


    def filtrar_imagenes(self, texto):
        texto = texto.lower().strip()
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            if item is not None:
                coincide = re.match(texto, item.text().lower())
                item.setHidden(not coincide)

    def mostrar_busqueda(self, lista: list):
        self.lista_imagenes.clear()
        self.cargar_datos(lista)
        '''for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            if item is not None:
                item.setHidden(True)

        for dic in lista:
            item = QListWidgetItem(QIcon(dic["imagen"]), dic["nombre"])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, dic["nombre"])
            self.lista_imagenes.addItem(item)'''

    def mostrar_pendrives(self, pendrives: list):
        seleccion_previa = self.box_pendrives.currentText()
        self.box_pendrives.clear()

        if not pendrives:
            self.senal_pendrive_seleccionado.emit("")
            return

        for pendrive in pendrives:
            self.box_pendrives.addItem(pendrive, pendrive)

        # Mantiene seleccionado el pendrive que estaba elegido si sigue conectado
        indice = self.box_pendrives.findText(seleccion_previa)
        if indice >= 0:
            self.box_pendrives.setCurrentIndex(indice)

    def agregar_elementos_seleccionados(self):
        items_marcados = self.lista_imagenes.selectedItems()
        if not items_marcados:
            QMessageBox.warning(self, "Atención", "Debes seleccionar al menos una matriz para añadirla")
            return

        ya_agregados = [
            item.text()
            for i in range(self.lista_seleccionados.count())
            if (item := self.lista_seleccionados.item(i)) is not None
        ]

        for item in items_marcados:
            nuevo_item = item.clone()
            if nuevo_item != None and not nuevo_item.text() in ya_agregados:
                self.lista_seleccionados.addItem(nuevo_item)
            else:
                QMessageBox.warning(self, "Atención", "La matriz seleccionada es nula o ya esta seleccionada")
        self.lista_imagenes.clearSelection()

    def eliminar_seleccionada(self, item):
        fila = self.lista_seleccionados.row(item)
        self.lista_seleccionados.takeItem(fila)

    def accion_anadir_matrices_pendrive(self):
        if self.box_pendrives.count() == 0:
            self.mostrar_error_ventana_pendrive()
            return

        lista_nombres_seleccionados = [
            item.text()
            for i in range(self.lista_seleccionados.count())
            if (item := self.lista_seleccionados.item(i)) is not None
        ]
        if not lista_nombres_seleccionados:
            QMessageBox.warning(self, "Atención", "Debes tener al menos una matriz en seleccionada para mandarla al pendrive")
            return
        self.senal_matrices_seleccionadas.emit(lista_nombres_seleccionados)
        