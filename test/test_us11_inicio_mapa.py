import unittest
from game_state import Juego


class TestInicioMapa(unittest.TestCase):
    def test_creacion_con_starter_y_oro(self):
        j = Juego()
        msg = j.crear_jugador("Misty", criatura_inicial="Torrente", oro_inicial=350)
        self.assertIn("Torrente", msg)
        self.assertEqual(j.jugador.oro, 350)
        self.assertEqual(j.jugador.equipo[0].nombre, "Torrente")

    def test_mini_mapa_marca_posicion(self):
        j = Juego()
        j.crear_jugador("Red")
        mapa = j.mini_mapa()
        self.assertIn("[X] Pradera", mapa)
        j.mover("norte")
        mapa = j.mini_mapa()
        self.assertIn("[X] Volcán", mapa)


if __name__ == '__main__':
    unittest.main()
