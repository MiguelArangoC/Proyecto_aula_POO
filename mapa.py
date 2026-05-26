"""
mapa.py
=======
Define las clases Zona y Mapa, que representan la estructura
de navegación del mundo del juego.

- Zona: representa un área geográfica con criaturas y clima propios.
- Mapa: gestiona las zonas y las conexiones de navegación entre ellas.
"""

import random
from excepciones import ZonaInexistenteError


class Zona:
    """
    Representa una zona geográfica del mapa del juego.

    Atributos:
        nombre (str):              Nombre identificador de la zona.
        clima_base (str):          Clima predominante (ej. 'Soleado').
        criaturas_salvajes (list): Nombres de criaturas que pueden aparecer.
        conexiones (dict):         {dirección: nombre_zona_destino}
    """

    def __init__(self, nombre, clima_base, criaturas_salvajes, conexiones=None):
        if not nombre.strip():
            raise ValueError("El nombre de la zona no puede estar vacío.")

        self.nombre             = nombre
        self.clima_base         = clima_base
        self.criaturas_salvajes = criaturas_salvajes
        if conexiones is None:
            self.conexiones = {}
        else:
            self.conexiones = conexiones

    def agregar_conexion(self, direccion, nombre_zona):
        """Agrega o actualiza una conexión desde esta zona hacia otra."""
        self.conexiones[direccion] = nombre_zona

    def obtener_criatura_aleatoria(self):
        """
        Retorna el nombre de una criatura salvaje aleatoria de la zona.
        Retorna None si la lista está vacía.
        """
        if not self.criaturas_salvajes:
            return None
        return random.choice(self.criaturas_salvajes)

    def __repr__(self):
        return (
            f"Zona(nombre='{self.nombre}', clima='{self.clima_base}', "
            f"conexiones={list(self.conexiones.keys())})"
        )

    def __str__(self):
        dirs_ = ", ".join(f"{d} -> {z}" for d, z in self.conexiones.items())
        return f"{self.nombre} [{self.clima_base}] | Salidas: {dirs_ or 'ninguna'}"


class Mapa:
    """
    Gestiona la colección de zonas y las conexiones de navegación.
    """

    def __init__(self):
        self.zonas = {}   # dict {nombre_zona: objeto Zona}

    def agregar_zona(self, zona):
        """Registra una zona en el mapa."""
        self.zonas[zona.nombre] = zona

    def obtener_zona(self, nombre):
        """
        Busca y retorna una zona por su nombre.
        Lanza ZonaInexistenteError si no existe.
        """
        if nombre not in self.zonas:
            raise ZonaInexistenteError(
                f"La zona '{nombre}' no existe en el mapa.",
                nombre,
            )
        return self.zonas[nombre]

    def zonas_adyacentes(self, nombre):
        """
        Retorna las zonas accesibles desde una zona dada.
        Lanza ZonaInexistenteError si la zona origen no existe.
        """
        return self.obtener_zona(nombre).conexiones

    def __repr__(self):
        return f"Mapa(zonas={list(self.zonas.keys())})"

    def __str__(self):
        lineas = ["=== MAPA DEL MUNDO ==="]
        for zona in self.zonas.values():
            lineas.append(f"  {zona}")
        return "\n".join(lineas)


def crear_mapa_default():
    """
    Crea y retorna el mapa por defecto del juego con todas sus zonas.
    Se usa como función normal en lugar de método de clase.
    """
    mapa = Mapa()

    zonas_data = [
        Zona(
            nombre="Pradera",
            clima_base="Soleado",
            criaturas_salvajes=["Ignis", "Torrente"],
            conexiones={"norte": "Volcán", "este": "Lago"},
        ),
        Zona(
            nombre="Volcán",
            clima_base="Caluroso",
            criaturas_salvajes=["Ignis", "Rocafer"],
            conexiones={"sur": "Pradera", "este": "Cueva de Roca"},
        ),
        Zona(
            nombre="Lago",
            clima_base="Lluvioso",
            criaturas_salvajes=["Torrente", "Voltex"],
            conexiones={"oeste": "Pradera"},
        ),
        Zona(
            nombre="Cueva de Roca",
            clima_base="Tormentoso",
            criaturas_salvajes=["Rocafer", "Voltex"],
            conexiones={"oeste": "Volcán", "norte": "Cumbre Nevada"},
        ),
        Zona(
            nombre="Cumbre Nevada",
            clima_base="Nevado",
            criaturas_salvajes=["Glacius", "Voltex"],
            conexiones={"sur": "Cueva de Roca"},
        ),
    ]

    for zona in zonas_data:
        mapa.agregar_zona(zona)

    return mapa
