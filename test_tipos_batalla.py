import unittest
from unittest.mock import patch

from batalla import Batalla
from criatura import Criatura
from jugador import Jugador
from tipo import TIPOS_VALIDOS, Tipo


class TestTipoMultiplicadores(unittest.TestCase):
    def test_cruces_tipo_positivos_y_neutros(self):
        fuego = Tipo("Fuego")
        agua = Tipo("Agua")
        tierra = Tipo("Tierra")
        normal = Tipo("Normal")

        self.assertEqual(fuego.calcular_multiplicador(tierra), 1.5)
        self.assertEqual(agua.calcular_multiplicador(fuego), 1.5)
        self.assertEqual(normal.calcular_multiplicador(agua), 1.0)
        self.assertEqual(tierra.calcular_multiplicador(agua), 1.0)

    def test_todos_los_tipos_devuelven_valores_validos(self):
        valores_validos = {1.5, 1.0, 0.67}
        for atacante_nombre in TIPOS_VALIDOS:
            atacante = Tipo(atacante_nombre)
            for defensor_nombre in TIPOS_VALIDOS:
                defensor = Tipo(defensor_nombre)
                mult = atacante.calcular_multiplicador(defensor)
                self.assertIn(mult, valores_validos)


class TestBatallaTipoIntegrado(unittest.TestCase):
    @patch("batalla.random.randint", return_value=100)
    @patch("batalla.random.random", return_value=0.0)
    def test_batalla_invoca_multiplicador_tipo(self, _mock_random, _mock_randint):
        atacante = Criatura("Flama", "Fuego", hp=200, atk=100, defensa=1, velocidad=20, precision=1.0)
        defensor = Criatura("Roca", "Tierra", hp=200, atk=1, defensa=1, velocidad=1, precision=0.0)

        jugador = Jugador("Test")
        jugador.agregar_criatura(atacante)
        batalla = Batalla(jugador, defensor, nombre_clima="Soleado")

        with patch.object(atacante.tipo, "calcular_multiplicador", wraps=atacante.tipo.calcular_multiplicador) as spy:
            batalla.ejecutar_turno()
            self.assertTrue(spy.called)

        # Daño esperado: int(100 * 1.5) - 0 = 150
        self.assertEqual(defensor.hp, 50)


if __name__ == "__main__":
    unittest.main()
