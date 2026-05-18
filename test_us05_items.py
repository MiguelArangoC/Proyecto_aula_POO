"""
test_us05_items.py
==================
Pruebas unitarias para la Historia de Usuario 05:
  "Como jugador, quiero equipar ítems a mis criaturas para obtener
   ventajas con consecuencias reales en combate."

Criterios de aceptación verificados
-------------------------------------
✓ CA-1  Solo se puede equipar un ítem por criatura a la vez.
✓ CA-2  Equipar un ítem aplica el efecto positivo y el negativo de forma inmediata.
✓ CA-3  Cambiar el ítem revierte el anterior antes de aplicar el nuevo.
✓ CA-4  Si el jugador no tiene el ítem en inventario, se lanza ItemNoDisponibleError.
"""

import unittest

from criatura import Criatura
from item import Item
from jugador import Jugador
from excepciones import ItemNoDisponibleError, CriaturaDebilitadaError


def _criatura(nombre="Ignis", tipo="Fuego", hp=100, atk=50,
              defensa=10, velocidad=10, precision=0.9) -> Criatura:
    return Criatura(nombre, tipo, hp=hp, atk=atk,
                    defensa=defensa, velocidad=velocidad, precision=precision)


def _item(nombre="Espada", pos=None, neg=None) -> Item:
    return Item(
        nombre=nombre,
        descripcion="Ítem de prueba",
        efecto_positivo=pos or {"atk": 10},
        efecto_negativo=neg or {"velocidad": 5},
    )


# ─────────────────────────────────────────────────────────────────────────────
# CA-2: Equipar aplica efectos de inmediato
# ─────────────────────────────────────────────────────────────────────────────

class TestEquiparItemEfectos(unittest.TestCase):
    """Verifica que los efectos positivos y negativos se aplican al equipar."""

    def test_efecto_positivo_aumenta_estadistica(self):
        c = _criatura()
        atk_inicial = c.atk
        j = Jugador("Test")
        j.agregar_criatura(c)
        item = _item(pos={"atk": 10}, neg={})
        j.agregar_item(item)

        j.equipar_item(c, "Espada")

        self.assertEqual(c.atk, atk_inicial + 10)

    def test_efecto_negativo_reduce_estadistica(self):
        c = _criatura()
        vel_inicial = c.velocidad
        j = Jugador("Test")
        j.agregar_criatura(c)
        item = _item(pos={}, neg={"velocidad": 5})
        j.agregar_item(item)

        j.equipar_item(c, "Espada")

        self.assertEqual(c.velocidad, vel_inicial - 5)

    def test_ambos_efectos_aplicados(self):
        c = _criatura(atk=50, velocidad=10)
        j = Jugador("Test")
        j.agregar_criatura(c)
        item = _item(pos={"atk": 15}, neg={"velocidad": 3})
        j.agregar_item(item)

        j.equipar_item(c, "Espada")

        self.assertEqual(c.atk, 65)
        self.assertEqual(c.velocidad, 7)


# ─────────────────────────────────────────────────────────────────────────────
# CA-1: Solo un ítem por criatura
# ─────────────────────────────────────────────────────────────────────────────

class TestUnItemPorCriatura(unittest.TestCase):
    """Verifica que cada criatura solo puede tener un ítem equipado a la vez."""

    def test_item_equipado_registrado(self):
        c = _criatura()
        j = Jugador("Test")
        j.agregar_criatura(c)
        item = _item()
        j.agregar_item(item)

        j.equipar_item(c, "Espada")

        self.assertIsNotNone(c.item_equipado)
        self.assertEqual(c.item_equipado.nombre, "Espada")

    def test_sin_item_equipado_es_none(self):
        c = _criatura()
        self.assertIsNone(c.item_equipado)


# ─────────────────────────────────────────────────────────────────────────────
# CA-3: Cambiar ítem revierte el anterior
# ─────────────────────────────────────────────────────────────────────────────

class TestCambioDeItem(unittest.TestCase):
    """Verifica que al cambiar el ítem se revierte el efecto del anterior."""

    def test_cambio_de_item_revierte_anterior(self):
        c = _criatura(atk=50)
        j = Jugador("Test")
        j.agregar_criatura(c)

        item1 = Item("Espada1", "desc", efecto_positivo={"atk": 10},
                     efecto_negativo={})
        item2 = Item("Espada2", "desc", efecto_positivo={"atk": 20},
                     efecto_negativo={})
        j.agregar_item(item1)
        j.agregar_item(item2)

        j.equipar_item(c, "Espada1")
        self.assertEqual(c.atk, 60)      # +10

        j.equipar_item(c, "Espada2")
        self.assertEqual(c.atk, 70)      # revertido +10, aplicado +20 → 50+20

    def test_item_equipado_cambia_referencia(self):
        c = _criatura()
        j = Jugador("Test")
        j.agregar_criatura(c)

        item1 = Item("A", "d", efecto_positivo={}, efecto_negativo={})
        item2 = Item("B", "d", efecto_positivo={}, efecto_negativo={})
        j.agregar_item(item1)
        j.agregar_item(item2)

        j.equipar_item(c, "A")
        self.assertEqual(c.item_equipado.nombre, "A")

        j.equipar_item(c, "B")
        self.assertEqual(c.item_equipado.nombre, "B")


# ─────────────────────────────────────────────────────────────────────────────
# CA-4: ItemNoDisponibleError si el ítem no está en inventario
# ─────────────────────────────────────────────────────────────────────────────

class TestItemNoEnInventario(unittest.TestCase):
    """Verifica que se lanza ItemNoDisponibleError si el ítem no existe."""

    def test_item_inexistente_lanza_excepcion(self):
        c = _criatura()
        j = Jugador("Test")
        j.agregar_criatura(c)

        with self.assertRaises(ItemNoDisponibleError):
            j.equipar_item(c, "ItemQueNoExiste")

    def test_excepcion_indica_nombre_del_item(self):
        c = _criatura()
        j = Jugador("Test")
        j.agregar_criatura(c)

        with self.assertRaises(ItemNoDisponibleError) as ctx:
            j.equipar_item(c, "Pocion")
        self.assertEqual(ctx.exception.nombre_item, "Pocion")

    def test_criatura_debilitada_lanza_excepcion(self):
        c = _criatura(hp=1)
        c.hp = 0   # debilitar manualmente
        j = Jugador("Test")
        j.agregar_criatura(c)
        item = _item()
        j.agregar_item(item)

        with self.assertRaises(CriaturaDebilitadaError):
            j.equipar_item(c, "Espada")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
