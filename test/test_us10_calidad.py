"""
test_us10_calidad.py
====================
Pruebas para US-10: calidad del código (docstrings, excepciones, módulos limpios).
"""

import unittest
import inspect

from criatura import Criatura
from jugador import Jugador
from batalla import Batalla, EstadoBatalla
from condicion_climatica import CondicionClimatica
from tipo import Tipo
from item import Item
from mapa import Zona, Mapa
from excepciones import (
    GameError, EquipoLlenoError, CapturaFallidaError,
    ItemNoDisponibleError, CriaturaDebilitadaError,
    PartidaNoEncontradaError, ZonaInexistenteError,
)


def _metodos_publicos(cls):
    """Retorna los métodos públicos (no dunder) de una clase."""
    return [
        (name, obj) for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction)
        if not name.startswith("_")
    ]


class TestDocstringClases(unittest.TestCase):
    """Verifica que todas las clases principales tienen docstring."""

    def _check(self, cls):
        self.assertIsNotNone(cls.__doc__,
                             f"{cls.__name__} debe tener docstring de clase")

    def test_criatura_docstring(self): self._check(Criatura)
    def test_jugador_docstring(self): self._check(Jugador)
    def test_batalla_docstring(self): self._check(Batalla)
    def test_condicion_climatica_docstring(self): self._check(CondicionClimatica)
    def test_tipo_docstring(self): self._check(Tipo)
    def test_item_docstring(self): self._check(Item)
    def test_zona_docstring(self): self._check(Zona)
    def test_mapa_docstring(self): self._check(Mapa)


class TestDocstringMetodos(unittest.TestCase):
    """Verifica que los métodos públicos importantes tienen docstring."""

    CLASES = [Criatura, Jugador, Batalla, CondicionClimatica, Tipo, Item, Zona, Mapa]

    def test_metodos_publicos_tienen_docstring(self):
        sin_doc = []
        for cls in self.CLASES:
            for nombre, metodo in _metodos_publicos(cls):
                if metodo.__doc__ is None:
                    sin_doc.append(f"{cls.__name__}.{nombre}")
        self.assertEqual(sin_doc, [],
                         f"Métodos sin docstring: {sin_doc}")


class TestExcepcionesHerencia(unittest.TestCase):
    """Verifica que todas las excepciones heredan de GameError."""

    EXCEPCIONES = [
        EquipoLlenoError, CapturaFallidaError, ItemNoDisponibleError,
        CriaturaDebilitadaError, PartidaNoEncontradaError, ZonaInexistenteError,
    ]

    def test_todas_heredan_de_game_error(self):
        for exc in self.EXCEPCIONES:
            self.assertTrue(
                issubclass(exc, GameError),
                f"{exc.__name__} debe heredar de GameError"
            )

    def test_excepciones_guardan_atributos(self):
        e1 = EquipoLlenoError("msg", 6)
        self.assertEqual(e1.capacidad_maxima, 6)

        e2 = CapturaFallidaError("msg", "Ignis")
        self.assertEqual(e2.nombre_criatura, "Ignis")

        e3 = ItemNoDisponibleError("msg", "Pocion")
        self.assertEqual(e3.nombre_item, "Pocion")

        e4 = CriaturaDebilitadaError("msg", "Torrente")
        self.assertEqual(e4.nombre_criatura, "Torrente")

        e5 = PartidaNoEncontradaError("msg", "partida.json")
        self.assertEqual(e5.ruta, "partida.json")

        e6 = ZonaInexistenteError("msg", "Desierto")
        self.assertEqual(e6.nombre_zona, "Desierto")


class TestModulosImportanSinError(unittest.TestCase):
    """Verifica que todos los módulos importan sin errores."""

    def test_importaciones_ok(self):
        # Si algún módulo fallara, el import arriba habría lanzado excepción
        for cls in [Criatura, Jugador, Batalla, CondicionClimatica,
                    Tipo, Item, Zona, Mapa]:
            self.assertIsNotNone(cls)


class TestNoHayPassSinImplementar(unittest.TestCase):
    """Verifica que los métodos principales no usan 'pass' como cuerpo único."""

    CLASES = [Criatura, Jugador, Batalla, CondicionClimatica, Tipo, Item]

    def test_metodos_no_son_solo_pass(self):
        vacios = []
        for cls in self.CLASES:
            for nombre, metodo in _metodos_publicos(cls):
                try:
                    src = inspect.getsource(metodo).strip()
                    lineas = [l.strip() for l in src.split("\n")
                              if l.strip() and not l.strip().startswith("#")
                              and not l.strip().startswith('"""')
                              and not l.strip().startswith("'\"'\"'")]
                    if lineas == ["pass"]:
                        vacios.append(f"{cls.__name__}.{nombre}")
                except (OSError, TypeError):
                    pass
        self.assertEqual(vacios, [],
                         f"Métodos sin implementar (solo pass): {vacios}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
