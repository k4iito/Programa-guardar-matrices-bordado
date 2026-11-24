from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QObject, QThread, QTimer
import os
import pyembroidery as em
import json
import re
import string 
import ctypes
import shutil
import sys

class matriz:
    def __init__(self, ruta: str, ruta_imagen=None, nombre=None):
        self.ruta = ruta
        self.carpeta = os.path.dirname(ruta)
        if nombre == None:
            self.nombre, self.extension = os.path.splitext(os.path.basename(ruta))
        else:
            self.nombre = nombre
        if ruta_imagen == None:
            try:
                em.convert(ruta, f"imagenes\\{self.nombre}.png")
            except Exception as error:
                print(f"algo fallo, error {error}")

            self.ruta_imagen = f"imagenes\\{self.nombre}.png" 
        else:
            self.ruta_imagen = ruta_imagen
        self.nombre_imagen = f"{self.nombre}.png"

    def cambiar_nombre(self, nombre: str) -> str:
        self.nombre = nombre
        return "nombre actualizado"

class matrizEnconder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, matriz):
            return {
                "tipo" : "matriz",
                "nombre" : obj.nombre,
                "ruta" : obj.ruta,
                "ruta_imagen" : obj.ruta_imagen
            }
        return super().default(obj)

def funcion_matriz_hook(diccionario: dict):
    if diccionario.get("tipo") != "matriz":
        return diccionario
    return matriz(
        ruta = diccionario["ruta"],
        nombre = diccionario["nombre"],
        ruta_imagen = diccionario["ruta_imagen"]
    )

class CargarImagenes(QThread):
    senal_matriz = pyqtSignal(list)
    senal_base_datos = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.carpeta_actual = os.path.dirname(sys.executable)
        else:
            self.carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        self.carpeta_matrices = os.path.join(self.carpeta_actual, "matrices")
        self.ruta_BD = os.path.join(self.carpeta_actual, "matrices.json")
        self.base_datos = {}

    def run(self):
        self.cargar_datos()
        self.senal_base_datos.emit(self.base_datos)
        while True:

            ya_procesados = set(self.base_datos["matrices_procesadas"])
            hubo_cambios = False
            anadir = []

            for archivo_matriz in os.listdir(self.carpeta_matrices):
                nombre, extension = os.path.splitext(
                    os.path.basename(os.path.join(self.carpeta_matrices, archivo_matriz))
                    )
                ruta_archivo = os.path.join(self.carpeta_matrices, archivo_matriz)
                if not os.path.isfile(ruta_archivo) or nombre.lower() in ya_procesados or extension.lower() not in [".jef"]:
                    continue
                anadir.append(os.path.join(self.carpeta_matrices, archivo_matriz))
                ya_procesados.add(nombre.lower())
                self.base_datos["matrices_procesadas"].append(nombre.lower())
                hubo_cambios = True

            if hubo_cambios:
                for ruta in anadir:
                    self.agregar_matriz(ruta)
                self.guardar_base_datos()
                self.senal_base_datos.emit(self.base_datos)

            self.msleep(1000)

    def cargar_datos(self):
        if not os.path.exists(self.ruta_BD):
            return {"matrices_procesadas" : [], "matrices" : []}
            
        with open(self.ruta_BD, "r", encoding="utf-8") as archivo:
            self.base_datos = json.load(archivo, object_hook=funcion_matriz_hook)

    def agregar_matriz(self, archivo_matriz):
        nueva_matriz = matriz(archivo_matriz)
        self.senal_matriz.emit([{"nombre": nueva_matriz.nombre, "imagen" : nueva_matriz.ruta_imagen}])
        self.base_datos["matrices"].append(nueva_matriz)

    def guardar_base_datos(self):
        with open(self.ruta_BD, "w", encoding="utf-8") as archivo:
            json.dump(self.base_datos, archivo, cls=matrizEnconder ,indent=4, ensure_ascii=False)



class backend(QObject):
    senal_enviar_busqueda = pyqtSignal(list) # lista de matrices coincidentes
    senal_enviar_datos = pyqtSignal(list)
    senal_enviar_pendrives = pyqtSignal(list)

    
    def __init__(self):
        super().__init__()
        self.base_datos = {}
        self.primer_inicio = True
        self.pendrive_conectado = False
        self.ruta_pendrive = ""

    def iniciar(self):
        if not os.path.exists("matrices.json"):
            shutil.copy("matrices.example.json", "matrices.json")
        self.threadProcesar = CargarImagenes()
        self.threadProcesar.senal_matriz.connect(self.matriz_nueva)
        self.threadProcesar.senal_base_datos.connect(self.actualizar_base_datos)
        self.threadProcesar.start()
        self.timer_pendrive = QTimer(self)
        self.timer_pendrive.timeout.connect(self.buscar_pendrives)
        self.timer_pendrive.start(2000)


    def buscar_pendrives(self):
        DRIVE_REMOVABLE = 2

        pendrives = []
        for letra in string.ascii_uppercase:
            unidad = f"{letra}:\\"
            if os.path.exists(unidad):
                tipo = ctypes.windll.kernel32.GetDriveTypeW(unidad)
                if tipo == DRIVE_REMOVABLE:
                    self.pendrive_conectado = True
                    pendrives.append(unidad)
        if len(pendrives) > 0:
            self.timer_pendrive.setInterval(5000)
        for pendrive in pendrives:
            if not pendrive == self.pendrive_seleccionado:
                self.senal_enviar_pendrives.emit(pendrives)
                return

    def matriz_nueva(self, lista: list):
        self.senal_enviar_datos.emit(lista)

    def actualizar_base_datos(self, base_datos: dict):
        self.base_datos = base_datos
        if self.primer_inicio:
            matrices_enviar = []
            for matriz in self.base_datos["matrices"]:
                matrices_enviar.append({"nombre": matriz.nombre, "imagen" : matriz.ruta_imagen})
            self.senal_enviar_busqueda.emit(matrices_enviar)
            self.primer_inicio = False

    
    def buscar_por_nombre(self, nombre :str):
        if len(self.base_datos["matrices"]) == 0:
            self.senal_enviar_busqueda.emit([])
        matrices_coincidentes = []
        nombre = nombre.lower()
        for matriz in self.base_datos["matrices"]:
            if re.match(nombre, matriz.nombre.lower()):
                matrices_coincidentes.append({"nombre": matriz.nombre, "imagen" : matriz.ruta_imagen})

        self.senal_enviar_busqueda.emit(matrices_coincidentes)

    def pendrive_seleccionado(self, ruta: str):
        self.ruta_pendrive = ruta
        print(f"pendrive seleccionado: {ruta}")
    
    def vaciar_pendrive(self):
        print(f"vaciar pendrive {self.ruta_pendrive}") # pendiente colocar que se borra
        carpeta = self.ruta_pendrive + "EMB\\embf"
        for nombre_archivo in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, nombre_archivo)
            if os.path.isfile(ruta_completa):
                os.remove(ruta_completa)

    def guardar_matrices_pendrive(self, lista : list):
        print(F"guardar matrices {lista}")
        ruta_matrices = {matriz.nombre : matriz.ruta for matriz in self.base_datos["matrices"]}
        carpeta = os.path.join(self.ruta_pendrive, "EMB", "embf")

        os.makedirs(carpeta, exist_ok=True)

        for nombre in lista:
            ruta = ruta_matrices.get(nombre)
            if ruta and os.path.isfile(ruta):
                shutil.copy(ruta, carpeta)
