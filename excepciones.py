"""
excepciones.py
==============
Excepciones personalizadas del juego de Criaturas por Turnos.
Todas heredan de la clase base GameError para poder capturarlas
con un solo except si se necesita.
"""


class GameError(Exception):
    """Clase base de todas las excepciones del juego."""
    pass


class EquipoLlenoError(GameError):
    """Se lanza cuando el equipo ya tiene el máximo de criaturas (6)."""

    def __init__(self, mensaje, capacidad_maxima):
        super().__init__(mensaje)
        self.capacidad_maxima = capacidad_maxima


class CapturaFallidaError(GameError):
    """Se lanza cuando el intento de captura falla."""

    def __init__(self, mensaje, nombre_criatura):
        super().__init__(mensaje)
        self.nombre_criatura = nombre_criatura


class ItemNoDisponibleError(GameError):
    """Se lanza cuando el ítem pedido no está en el inventario."""

    def __init__(self, mensaje, nombre_item):
        super().__init__(mensaje)
        self.nombre_item = nombre_item


class CriaturaDebilitadaError(GameError):
    """Se lanza cuando se intenta usar una criatura con HP = 0."""

    def __init__(self, mensaje, nombre_criatura):
        super().__init__(mensaje)
        self.nombre_criatura = nombre_criatura


class PartidaNoEncontradaError(GameError):
    """Se lanza cuando no se encuentra el archivo de guardado."""

    def __init__(self, mensaje, ruta):
        super().__init__(mensaje)
        self.ruta = ruta


class ZonaInexistenteError(GameError):
    """Se lanza cuando se intenta acceder a una zona que no existe."""

    def __init__(self, mensaje, nombre_zona):
        super().__init__(mensaje)
        self.nombre_zona = nombre_zona
