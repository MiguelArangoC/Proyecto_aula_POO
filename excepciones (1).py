"""
excepciones.py
==============
Módulo de excepciones personalizadas del juego de Criaturas por Turnos.
Todas las excepciones heredan de GameError y almacenan sus parámetros
como atributos de instancia para que el código que las captura pueda
acceder a ellos sin parsear el mensaje.
"""


class GameError(Exception):
    """Clase base de todas las excepciones del juego."""


class EquipoLlenoError(GameError):
    """
    Se lanza cuando el jugador intenta agregar una criatura a su equipo
    pero ya tiene el máximo permitido (6 criaturas).

    Atributos:
        mensaje (str): Descripción del error.
        capacidad_maxima (int): Límite de criaturas permitido.

    Ejemplo de uso:
        raise EquipoLlenoError("El equipo ya tiene 6 criaturas.", capacidad_maxima=6)
    """

    def __init__(self, mensaje: str, capacidad_maxima: int) -> None:
        super().__init__(mensaje)
        self.capacidad_maxima: int = capacidad_maxima


class CapturaFallidaError(GameError):
    """
    Se lanza cuando un intento de captura de una criatura salvaje falla
    (por probabilidad o por falta de ítem adecuado).

    Atributos:
        mensaje (str): Descripción del motivo del fallo.
        nombre_criatura (str): Nombre de la criatura que no pudo capturarse.

    Ejemplo de uso:
        raise CapturaFallidaError("La criatura escapó.", nombre_criatura="Torrente")
    """

    def __init__(self, mensaje: str, nombre_criatura: str) -> None:
        super().__init__(mensaje)
        self.nombre_criatura: str = nombre_criatura


class ItemNoDisponibleError(GameError):
    """
    Se lanza cuando el jugador intenta usar un ítem que no está en su inventario.

    Atributos:
        mensaje (str): Descripción del error.
        nombre_item (str): Nombre del ítem que se intentó usar.

    Ejemplo de uso:
        raise ItemNoDisponibleError("Ítem no encontrado.", nombre_item="Poción")
    """

    def __init__(self, mensaje: str, nombre_item: str) -> None:
        super().__init__(mensaje)
        self.nombre_item: str = nombre_item


class CriaturaDebilitadaError(GameError):
    """
    Se lanza cuando se intenta usar en combate una criatura cuyo HP es 0 o menor.

    Atributos:
        mensaje (str): Descripción del error.
        nombre_criatura (str): Nombre de la criatura debilitada.

    Ejemplo de uso:
        raise CriaturaDebilitadaError("La criatura está debilitada.", nombre_criatura="Ignis")
    """

    def __init__(self, mensaje: str, nombre_criatura: str) -> None:
        super().__init__(mensaje)
        self.nombre_criatura: str = nombre_criatura


class PartidaNoEncontradaError(GameError):
    """
    Se lanza cuando se intenta cargar un archivo de guardado que no existe.

    Atributos:
        mensaje (str): Descripción del error.
        ruta (str): Ruta del archivo que no se encontró.

    Ejemplo de uso:
        raise PartidaNoEncontradaError("Archivo no encontrado.", ruta="partida.json")
    """

    def __init__(self, mensaje: str, ruta: str) -> None:
        super().__init__(mensaje)
        self.ruta: str = ruta


class ZonaInexistenteError(GameError):
    """
    Se lanza cuando se intenta acceder a una zona que no existe en el mapa.

    Atributos:
        mensaje (str): Descripción del error.
        nombre_zona (str): Nombre de la zona inválida.

    Ejemplo de uso:
        raise ZonaInexistenteError("Zona no encontrada.", nombre_zona="Desierto")
    """

    def __init__(self, mensaje: str, nombre_zona: str) -> None:
        super().__init__(mensaje)
        self.nombre_zona: str = nombre_zona
