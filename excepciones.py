"""
excepciones.py
==============
Módulo de excepciones personalizadas del juego de Criaturas por Turnos.
Todas las excepciones heredan de Exception y documentan su causa,
los parámetros relevantes y el contexto de lanzamiento.
"""


class EquipoLlenoError(Exception):
    """
    Se lanza cuando el jugador intenta agregar una criatura a su equipo
    pero ya tiene el máximo permitido (6 criaturas).

    Parámetros:
        mensaje (str): Descripción del error.
        capacidad_maxima (int): Límite de criaturas permitido.

    Ejemplo de uso:
        raise EquipoLlenoError("El equipo ya tiene 6 criaturas.", capacidad_maxima=6)
    """

    def __init__(self, mensaje: str = "El equipo está lleno.", capacidad_maxima: int = 6):
        self.capacidad_maxima = capacidad_maxima
        super().__init__(mensaje)


class CapturaFallidaError(Exception):
    """
    Se lanza cuando un intento de captura de una criatura salvaje falla
    (por probabilidad o por falta de ítem adecuado).

    Parámetros:
        mensaje (str): Descripción del motivo del fallo.
        nombre_criatura (str): Nombre de la criatura que no pudo capturarse.

    Ejemplo de uso:
        raise CapturaFallidaError("La criatura escapó.", nombre_criatura="Torrente")
    """

    def __init__(self, mensaje: str = "La captura falló.", nombre_criatura: str = ""):
        self.nombre_criatura = nombre_criatura
        super().__init__(mensaje)


class ItemNoDisponibleError(Exception):
    """
    Se lanza cuando el jugador intenta usar un ítem que no está en su inventario.

    Parámetros:
        mensaje (str): Descripción del error.
        nombre_item (str): Nombre del ítem que se intentó usar.

    Ejemplo de uso:
        raise ItemNoDisponibleError("Ítem no encontrado.", nombre_item="Poción")
    """

    def __init__(self, mensaje: str = "El ítem no está en el inventario.", nombre_item: str = ""):
        self.nombre_item = nombre_item
        super().__init__(mensaje)


class CriaturaDebilitadaError(Exception):
    """
    Se lanza cuando se intenta usar en combate una criatura cuyo HP es 0 o menor.

    Parámetros:
        mensaje (str): Descripción del error.
        nombre_criatura (str): Nombre de la criatura debilitada.

    Ejemplo de uso:
        raise CriaturaDebilitadaError("La criatura está debilitada.", nombre_criatura="Ignis")
    """

    def __init__(self, mensaje: str = "La criatura está debilitada y no puede luchar.", nombre_criatura: str = ""):
        self.nombre_criatura = nombre_criatura
        super().__init__(mensaje)


class PartidaNoEncontradaError(Exception):
    """
    Se lanza cuando se intenta cargar un archivo de guardado que no existe.

    Parámetros:
        mensaje (str): Descripción del error.
        ruta (str): Ruta del archivo que no se encontró.

    Ejemplo de uso:
        raise PartidaNoEncontradaError("Archivo no encontrado.", ruta="partida.json")
    """

    def __init__(self, mensaje: str = "No se encontró el archivo de guardado.", ruta: str = ""):
        self.ruta = ruta
        super().__init__(mensaje)


class ZonaInexistenteError(Exception):
    """
    Se lanza cuando se intenta acceder a una zona que no existe en el mapa.

    Parámetros:
        mensaje (str): Descripción del error.
        nombre_zona (str): Nombre de la zona inválida.

    Ejemplo de uso:
        raise ZonaInexistenteError("Zona no encontrada.", nombre_zona="Desierto")
    """

    def __init__(self, mensaje: str = "La zona no existe en el mapa.", nombre_zona: str = ""):
        self.nombre_zona = nombre_zona
        super().__init__(mensaje)
