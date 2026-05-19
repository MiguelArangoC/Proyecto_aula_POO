"""
test_us06_captura.py
====================
Pruebas unitarias para la Historia de Usuario 06:
  "Como jugador, quiero capturar criaturas salvajes para ampliar mi equipo."

Criterios de aceptación verificados
-------------------------------------
✓ CA-1  La captura requiere un ítem de captura en el inventario.
✓ CA-2  Si el equipo tiene 6 criaturas, se lanza EquipoLlenoError.
✓ CA-3  La criatura capturada se agrega al equipo con sus estadísticas base.
✓ CA-4  El ítem de captura se consume del inventario al usarse (éxito o fallo).
✓ CA-5  Se maneja CapturaFallidaError cuando la probabilidad es baja.
"""

import unittest
from unittest.mock import patch

from criatura import Criatura
from item import Item
from jugador import Jugador
from excepciones import EquipoLlenoError, ItemNoDisponibleError, CapturaFallidaError


def _criatura_salvaje(nombre="Torrente", tipo="Agua", hp=100, atk=40) -> Criatura:
    return Criatura(nombre, tipo, hp=hp, atk=atk)


def _item_captura(nombre="PokeBall") -> Item:
    return Item(
        nombre=nombre,
        descripcion="Ítem de captura",
        efecto_positivo={},
        efecto_negativo={},
        es_consumible=True,
        es_captura=True,
    )


def _jugador_con_criatura(nombre="Ash") -> Jugador:
    j = Jugador(nombre)
    c = Criatura("Inicial", "Normal", hp=100, atk=30)
    j.agregar_criatura(c)
    return j


# ─────────────────────────────────────────────────────────────────────────────
# CA-1: Requiere ítem de captura
# ─────────────────────────────────────────────────────────────────────────────

class TestCapturaNecesitaItem(unittest.TestCase):
    """Verifica que capturar sin ítem lanza ItemNoDisponibleError."""

    def test_sin_item_lanza_excepcion(self):
        j = _jugador_con_criatura()
        salvaje = _criatura_salvaje()

        with self.assertRaises(ItemNoDisponibleError):
            j.capturar_criatura(salvaje, "PokeBall")

    def test_item_no_captura_lanza_excepcion(self):
        j = _jugador_con_criatura()
        salvaje = _criatura_salvaje()
        # Ítem normal, no de captura
        item_normal = Item("Pocion", "cura", {"hp": 30}, {}, es_captura=False)
        j.agregar_item(item_normal)

        with self.assertRaises(ItemNoDisponibleError):
            j.capturar_criatura(salvaje, "Pocion")


# ─────────────────────────────────────────────────────────────────────────────
# CA-2: EquipoLlenoError con 6 criaturas
# ─────────────────────────────────────────────────────────────────────────────

class TestEquipoLlenoAlCapturar(unittest.TestCase):
    """Verifica que se lanza EquipoLlenoError al intentar capturar con equipo lleno."""

    @patch("random.random", return_value=0.0)  # captura siempre exitosa
    def test_equipo_lleno_lanza_excepcion(self, _mock):
        j = Jugador("Ash")
        for i in range(6):
            j.agregar_criatura(Criatura(f"C{i}", "Normal", hp=50, atk=20))

        j.agregar_item(_item_captura())
        salvaje = _criatura_salvaje(hp=1)   # casi muerta → alta probabilidad

        with self.assertRaises(EquipoLlenoError):
            j.capturar_criatura(salvaje, "PokeBall")


# ─────────────────────────────────────────────────────────────────────────────
# CA-3 y CA-4: Captura exitosa
# ─────────────────────────────────────────────────────────────────────────────

class TestCapturaExitosa(unittest.TestCase):
    """Verifica que la criatura se agrega al equipo y el ítem se consume."""

    @patch("random.random", return_value=0.0)  # siempre captura
    def test_criatura_agregada_al_equipo(self, _mock):
        j = _jugador_con_criatura()
        salvaje = _criatura_salvaje()
        j.agregar_item(_item_captura())
        equipo_inicial = len(j.equipo)

        j.capturar_criatura(salvaje, "PokeBall")

        self.assertEqual(len(j.equipo), equipo_inicial + 1)
        self.assertIn(salvaje, j.equipo)

    @patch("random.random", return_value=0.0)  # siempre captura
    def test_item_consumido_tras_captura(self, _mock):
        j = _jugador_con_criatura()
        salvaje = _criatura_salvaje()
        j.agregar_item(_item_captura())
        self.assertTrue(j.tiene_item("PokeBall"))

        j.capturar_criatura(salvaje, "PokeBall")

        self.assertFalse(j.tiene_item("PokeBall"))

    @patch("random.random", return_value=0.0)  # siempre captura
    def test_estadisticas_base_preservadas(self, _mock):
        salvaje = _criatura_salvaje(hp=80, atk=45)
        j = _jugador_con_criatura()
        j.agregar_item(_item_captura())

        j.capturar_criatura(salvaje, "PokeBall")

        capturada = j.equipo[-1]
        self.assertEqual(capturada.atk, 45)
        self.assertEqual(capturada.hp_max, 80)


# ─────────────────────────────────────────────────────────────────────────────
# CA-4 (parcial): El ítem se consume incluso si la captura falla
# ─────────────────────────────────────────────────────────────────────────────

class TestItemConsumidoAlFallar(unittest.TestCase):
    """El ítem se consume del inventario incluso cuando la captura falla."""

    @patch("random.random", return_value=1.0)  # captura siempre falla
    def test_item_consumido_aunque_falle(self, _mock):
        j = _jugador_con_criatura()
        salvaje = _criatura_salvaje(hp=100)   # HP llena → probabilidad baja
        j.agregar_item(_item_captura())

        with self.assertRaises(CapturaFallidaError):
            j.capturar_criatura(salvaje, "PokeBall")

        self.assertFalse(j.tiene_item("PokeBall"),
                         "El ítem debe consumirse aunque la captura haya fallado")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
