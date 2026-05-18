"""
test_us07_progresion.py
=======================
Pruebas para US-07: experiencia y subida de nivel tras ganar batallas.
"""

import unittest
from unittest.mock import patch

from criatura import Criatura
from jugador import Jugador
from batalla import Batalla, EstadoBatalla


def _c(nombre="Héroe", tipo="Normal", hp=200, atk=100,
       defensa=1, velocidad=20, precision=1.0) -> Criatura:
    return Criatura(nombre, tipo, hp=hp, atk=atk,
                    defensa=defensa, velocidad=velocidad, precision=precision)


class TestGanarExperiencia(unittest.TestCase):
    def test_xp_acumulada(self):
        c = _c()
        c.ganar_experiencia(50)
        self.assertEqual(c.experiencia, 50)

    def test_xp_negativa_lanza_error(self):
        with self.assertRaises(ValueError):
            _c().ganar_experiencia(-10)

    def test_xp_cero_lanza_error(self):
        with self.assertRaises(ValueError):
            _c().ganar_experiencia(0)


class TestSubidaDeNivel(unittest.TestCase):
    def test_sube_nivel(self):
        c = _c()
        resultado = c.ganar_experiencia(100)
        self.assertTrue(resultado)
        self.assertEqual(c.nivel, 2)

    def test_hp_max_aumenta(self):
        c = _c(hp=100)
        hp_antes = c.hp_max
        c.ganar_experiencia(100)
        self.assertGreater(c.hp_max, hp_antes)

    def test_atk_aumenta(self):
        c = _c(atk=50)
        atk_antes = c.atk
        c.ganar_experiencia(100)
        self.assertGreater(c.atk, atk_antes)

    def test_defensa_aumenta(self):
        c = _c(defensa=20)   # int(20*1.05)=21
        def_antes = c.defensa
        c.ganar_experiencia(100)
        self.assertGreater(c.defensa, def_antes)

    def test_velocidad_aumenta(self):
        c = _c(velocidad=20)  # int(20*1.05)=21
        vel_antes = c.velocidad
        c.ganar_experiencia(100)
        self.assertGreater(c.velocidad, vel_antes)

    def test_hp_restaurado(self):
        c = _c(hp=100)
        c.hp = 10
        c.ganar_experiencia(100)
        self.assertEqual(c.hp, c.hp_max)

    def test_xp_sobrante_preservada(self):
        c = _c()
        c.ganar_experiencia(150)
        self.assertEqual(c.experiencia, 50)

    def test_no_sube_sin_xp(self):
        c = _c()
        resultado = c.ganar_experiencia(50)
        self.assertFalse(resultado)
        self.assertEqual(c.nivel, 1)


class TestMensajeNivelEnBatalla(unittest.TestCase):
    def test_log_nivel_tras_victoria(self):
        cj = _c("Flama", "Fuego", hp=200, atk=500,
                 defensa=1, velocidad=99, precision=1.0)
        ce = _c("Débil", "Normal", hp=1, atk=1, defensa=1,
                 velocidad=1, precision=0.0)
        cj.experiencia = 90

        j = Jugador("Ash")
        j.agregar_criatura(cj)
        batalla = Batalla(j, ce, nombre_clima="Soleado")

        with patch("batalla.random.random", return_value=0.0), \
             patch("batalla.random.randint", return_value=9999):
            estado = batalla.ejecutar_turno()

        self.assertEqual(estado, EstadoBatalla.VICTORIA)
        self.assertIn("nivel", " ".join(batalla.log).lower())


class TestNivelEnStr(unittest.TestCase):
    def test_nivel_en_str(self):
        c = _c()
        self.assertIn("Nv.1", str(c))

    def test_nivel_actualizado(self):
        c = _c()
        c.ganar_experiencia(100)
        self.assertIn("Nv.2", str(c))


if __name__ == "__main__":
    unittest.main(verbosity=2)
