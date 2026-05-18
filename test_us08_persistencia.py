"""
test_us08_persistencia.py
=========================
Pruebas para US-08: guardar y cargar partida en JSON.
"""

import json
import os
import tempfile
import unittest

from criatura import Criatura
from item import Item
from jugador import Jugador
from excepciones import PartidaNoEncontradaError


def _jugador_completo() -> Jugador:
    """Crea un jugador con criatura e ítem para pruebas de persistencia."""
    j = Jugador("Ash", "Volcán")
    c = Criatura("Ignis", "Fuego", hp=120, atk=60, defensa=15,
                 velocidad=12, precision=0.9, nivel=1)
    j.agregar_criatura(c)
    pocion = Item("Pocion", "Cura HP", {"hp": 30}, {}, es_consumible=True)
    j.agregar_item(pocion)
    return j


class TestGuardarPartida(unittest.TestCase):
    """Verifica que guardar() serializa correctamente el estado."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.ruta = self.tmp.name
        self.tmp.close()

    def tearDown(self):
        if os.path.exists(self.ruta):
            os.remove(self.ruta)

    def test_archivo_creado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        self.assertTrue(os.path.exists(self.ruta))

    def test_json_valido(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertIn("nombre", datos)
        self.assertIn("equipo", datos)
        self.assertIn("inventario", datos)

    def test_nombre_serializado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertEqual(datos["nombre"], "Ash")

    def test_posicion_serializada(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertEqual(datos["posicion"], "Volcán")

    def test_equipo_serializado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertEqual(len(datos["equipo"]), 1)
        self.assertEqual(datos["equipo"][0]["nombre"], "Ignis")

    def test_inventario_serializado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertEqual(len(datos["inventario"]), 1)
        self.assertEqual(datos["inventario"][0]["nombre"], "Pocion")


class TestCargarPartida(unittest.TestCase):
    """Verifica que cargar() restaura el estado exactamente."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.ruta = self.tmp.name
        self.tmp.close()

    def tearDown(self):
        if os.path.exists(self.ruta):
            os.remove(self.ruta)

    def test_estado_restaurado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        j2 = Jugador.cargar(self.ruta)

        self.assertEqual(j2.nombre, "Ash")
        self.assertEqual(j2.posicion, "Volcán")
        self.assertEqual(len(j2.equipo), 1)
        self.assertEqual(len(j2.inventario), 1)

    def test_criatura_restaurada(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        j2 = Jugador.cargar(self.ruta)
        c = j2.equipo[0]

        self.assertEqual(c.nombre, "Ignis")
        self.assertEqual(c.tipo.nombre, "Fuego")
        self.assertEqual(c.atk, 60)
        self.assertEqual(c.defensa, 15)

    def test_item_restaurado(self):
        j = _jugador_completo()
        j.guardar(self.ruta)
        j2 = Jugador.cargar(self.ruta)
        item = j2.inventario[0]

        self.assertEqual(item.nombre, "Pocion")
        self.assertTrue(item.es_consumible)

    def test_archivo_inexistente_lanza_error(self):
        with self.assertRaises(PartidaNoEncontradaError):
            Jugador.cargar("/ruta/que/no/existe.json")

    def test_error_indica_ruta(self):
        ruta_falsa = "/no/existe.json"
        with self.assertRaises(PartidaNoEncontradaError) as ctx:
            Jugador.cargar(ruta_falsa)
        self.assertIn(ruta_falsa, ctx.exception.ruta)

    def test_item_equipado_restaurado(self):
        """Si la criatura tenía un ítem equipado, debe restaurarse."""
        j = _jugador_completo()
        c = j.equipo[0]
        extra = Item("Escudo", "desc", {}, {"velocidad": 2})
        j.agregar_item(extra)
        j.equipar_item(c, "Escudo")
        j.guardar(self.ruta)

        j2 = Jugador.cargar(self.ruta)
        c2 = j2.equipo[0]
        self.assertIsNotNone(c2.item_equipado)
        self.assertEqual(c2.item_equipado.nombre, "Escudo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
