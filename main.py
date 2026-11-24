from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from frontend import frontend
from backend import backend

if '__main__' == __name__:
    applicacion = QApplication([])
    backend = backend()
    frontend = frontend()

    frontend.senal_buscar_por_nombre.connect(backend.buscar_por_nombre)
    frontend.senal_vaciar.connect(backend.vaciar_pendrive)
    frontend.senal_pendrive_seleccionado.connect(backend.pendrive_seleccionado)
    frontend.senal_matrices_seleccionadas.connect(backend.guardar_matrices_pendrive)

    backend.senal_enviar_busqueda.connect(frontend.mostrar_busqueda)
    backend.senal_enviar_datos.connect(frontend.cargar_datos)
    backend.senal_enviar_pendrives.connect(frontend.mostrar_pendrives)

    applicacion.setStyle("Fusion")
    paleta_oscura = QPalette()
    paleta_oscura.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    paleta_oscura.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Base, QColor(20, 20, 20))
    paleta_oscura.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    paleta_oscura.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    paleta_oscura.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    paleta_oscura.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    applicacion.setPalette(paleta_oscura)


    backend.iniciar()
    frontend.show()
    applicacion.exec()