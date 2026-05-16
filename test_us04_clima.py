"""
test_us04_clima.py
==================
Pruebas unitarias e integración para la Historia de Usuario 04:
  "Como jugador, quiero que el clima de la zona modifique el daño y la
   precisión en combate para que el entorno influya en la estrategia."

Criterios de aceptación verificados
-------------------------------------
✓ CA-1  modificador_ataque devuelve 1.20, 0.90 o 1.0 según corresponda.
✓ CA-2  El daño por turno se aplica correctamente (Fuego en Lluvia -5 HP/turno).
✓ CA-3  La batalla muestra el clima activo al inicio (RF9).
✓ CA-4  El clima cambia si la zona tiene condición base diferente.
✓ CA-5  Retornos y excepciones de modificador_ataque están documentados
        (se verifica que la función sea invocable, tenga docstring y lance
        ValueError ante clima inválido).
"""

import unittest
from unittest.mock import patch

from condicion_climatica import CondicionClimatica, CLIMAS_VALIDOS
from criatura import Criatura
from jugador import Jugador
from batalla import Batalla, EstadoBatalla


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _criatura(nombre: str, tipo: str, hp: int = 200, atk: int = 10,
              defensa: int = 1, velocidad: int = 10,
              precision: float = 1.0) -> Criatura:
    """Factoría rápida de Criatura para los tests."""
    return Criatura(nombre, tipo, hp=hp, atk=atk, defensa=defensa,
                    velocidad=velocidad, precision=precision)


def _batalla(clima: str,
             tipo_jugador: str = "Normal",
             tipo_enemigo: str = "Normal") -> tuple[Batalla, Criatura, Criatura]:
    """
    Crea una Batalla mínima con el clima indicado y devuelve
    (batalla, criatura_jugador, criatura_enemiga).
    """
    cj = _criatura("Héroe", tipo_jugador, hp=200, atk=50, velocidad=20)
    ce = _criatura("Villano", tipo_enemigo, hp=200, atk=1, velocidad=1,
                   precision=0.0)          # el enemigo siempre falla
    jugador = Jugador("Tester")
    jugador.agregar_criatura(cj)
    batalla = Batalla(jugador, ce, nombre_clima=clima)
    return batalla, cj, ce


# ─────────────────────────────────────────────────────────────────────────────
# CA-1  modificador_ataque devuelve 1.20, 0.90 o 1.0
# ─────────────────────────────────────────────────────────────────────────────

class TestModificadorAtaque(unittest.TestCase):
    """
    Verifica que CondicionClimatica.modificador_ataque retorne exactamente
    1.20 (beneficiado), 0.90 (perjudicado) o 1.0 (neutro) para todos los
    climas definidos.
    """

    def test_lluvioso_beneficia_agua(self):
        clima = CondicionClimatica("Lluvioso")
        self.assertAlmostEqual(clima.modificador_ataque("Agua"), 1.20)

    def test_lluvioso_perjudica_fuego(self):
        clima = CondicionClimatica("Lluvioso")
        self.assertAlmostEqual(clima.modificador_ataque("Fuego"), 0.90)

    def test_lluvioso_neutro_normal(self):
        clima = CondicionClimatica("Lluvioso")
        self.assertAlmostEqual(clima.modificador_ataque("Normal"), 1.0)

    def test_soleado_beneficia_fuego(self):
        clima = CondicionClimatica("Soleado")
        self.assertAlmostEqual(clima.modificador_ataque("Fuego"), 1.20)

    def test_soleado_perjudica_agua(self):
        clima = CondicionClimatica("Soleado")
        self.assertAlmostEqual(clima.modificador_ataque("Agua"), 0.90)

    def test_tormentoso_beneficia_rayo(self):
        clima = CondicionClimatica("Tormentoso")
        self.assertAlmostEqual(clima.modificador_ataque("Rayo"), 1.20)

    def test_tormentoso_perjudica_tierra(self):
        clima = CondicionClimatica("Tormentoso")
        self.assertAlmostEqual(clima.modificador_ataque("Tierra"), 0.90)

    def test_caluroso_beneficia_fuego_y_tierra(self):
        clima = CondicionClimatica("Caluroso")
        self.assertAlmostEqual(clima.modificador_ataque("Fuego"), 1.20)
        self.assertAlmostEqual(clima.modificador_ataque("Tierra"), 1.20)

    def test_caluroso_perjudica_agua(self):
        clima = CondicionClimatica("Caluroso")
        self.assertAlmostEqual(clima.modificador_ataque("Agua"), 0.90)

    def test_nevado_beneficia_agua(self):
        clima = CondicionClimatica("Nevado")
        self.assertAlmostEqual(clima.modificador_ataque("Agua"), 1.20)

    def test_nevado_perjudica_fuego_y_rayo(self):
        clima = CondicionClimatica("Nevado")
        self.assertAlmostEqual(clima.modificador_ataque("Fuego"), 0.90)
        self.assertAlmostEqual(clima.modificador_ataque("Rayo"), 0.90)

    def test_todos_retornan_valor_valido(self):
        """El modificador siempre es 1.20, 0.90 o 1.0 para todos los climas."""
        valores_validos = {1.20, 0.90, 1.0}
        tipos = ["Fuego", "Agua", "Tierra", "Rayo", "Normal"]
        for nombre_clima in CLIMAS_VALIDOS:
            clima = CondicionClimatica(nombre_clima)
            for tipo in tipos:
                resultado = clima.modificador_ataque(tipo)
                self.assertIn(
                    resultado, valores_validos,
                    f"Clima '{nombre_clima}', tipo '{tipo}' -> {resultado} no es válido"
                )


# ─────────────────────────────────────────────────────────────────────────────
# CA-2  Daño por turno: Fuego en Lluvia pierde 5 HP por turno
# ─────────────────────────────────────────────────────────────────────────────

class TestDanoPorTurno(unittest.TestCase):
    """
    Verifica que aplicar_dano_turno descuente los HP correctos cada turno.
    """

    def test_fuego_en_lluvia_pierde_5_hp(self):
        """Fuego bajo Lluvia debe recibir exactamente 5 de daño por turno."""
        clima = CondicionClimatica("Lluvioso")
        criatura = _criatura("Flama", "Fuego", hp=100)
        hp_inicial = criatura.hp

        dano = clima.aplicar_dano_turno(criatura)

        self.assertEqual(dano, 5, "El daño climático debe ser 5")
        self.assertEqual(criatura.hp, hp_inicial - 5,
                         "El HP debe reducirse exactamente 5 puntos")

    def test_agua_en_lluvia_no_recibe_dano(self):
        clima = CondicionClimatica("Lluvioso")
        criatura = _criatura("Torrente", "Agua", hp=100)

        dano = clima.aplicar_dano_turno(criatura)

        self.assertEqual(dano, 0)
        self.assertEqual(criatura.hp, 100)

    def test_tierra_en_tormenta_pierde_3_hp(self):
        clima = CondicionClimatica("Tormentoso")
        criatura = _criatura("Roca", "Tierra", hp=50)

        dano = clima.aplicar_dano_turno(criatura)

        self.assertEqual(dano, 3)
        self.assertEqual(criatura.hp, 47)

    def test_hp_no_baja_de_cero(self):
        """La HP nunca debe ser negativa por daño climático."""
        clima = CondicionClimatica("Lluvioso")
        criatura = _criatura("Ceniza", "Fuego", hp=3)

        clima.aplicar_dano_turno(criatura)

        self.assertGreaterEqual(criatura.hp, 0,
                                "El HP no debe ser negativo tras daño climático")

    @patch("batalla.random.random", return_value=0.95)   # 0.95 > precision → todos fallan
    def test_dano_clima_integrado_en_batalla(self, _mock_rand):
        """
        En una Batalla real, la criatura Fuego en clima Lluvioso debe
        sufrir exactamente 5 HP de daño climático al ejecutar_turno.
        Todos los ataques se anulan (precision < 0.95) para aislar el efecto del clima.
        """
        cj = _criatura("Salamandra", "Fuego", hp=100, atk=5, velocidad=20,
                        precision=0.90)   # 0.95 > 0.90 → jugador falla
        ce = _criatura("Rival", "Normal", hp=200, atk=1, velocidad=1,
                        precision=0.90)   # 0.95 > 0.90 → enemigo falla
        jugador = Jugador("Luis")
        jugador.agregar_criatura(cj)
        batalla = Batalla(jugador, ce, nombre_clima="Lluvioso")

        hp_antes = cj.hp
        batalla.ejecutar_turno()

        self.assertEqual(cj.hp, hp_antes - 5,
                         "La criatura Fuego debe perder exactamente 5 HP por clima Lluvioso")


# ─────────────────────────────────────────────────────────────────────────────
# CA-3  RF9: el log inicial de la batalla muestra el clima activo
# ─────────────────────────────────────────────────────────────────────────────

class TestRF9ClimaMostradoAlInicio(unittest.TestCase):
    """
    RF9: Al iniciar la batalla se registra en el log el clima activo,
    permitiendo al jugador conocer el entorno antes del primer turno.
    """

    def test_log_inicial_contiene_nombre_clima(self):
        batalla, _, _ = _batalla("Tormentoso")
        primer_mensaje = batalla.log[0]
        self.assertIn("Tormentoso", primer_mensaje,
                      "El log de inicio debe mencionar el nombre del clima")

    def test_log_inicial_contiene_nombre_enemigo(self):
        batalla, _, ce = _batalla("Nevado")
        self.assertIn(ce.nombre, batalla.log[0])

    def test_clima_en_resumen(self):
        """resumen() también expone el clima activo (para la UI del jugador)."""
        batalla, _, _ = _batalla("Soleado")
        self.assertIn("Soleado", batalla.resumen())

    def test_todos_los_climas_aparecen_en_log(self):
        for nombre_clima in CLIMAS_VALIDOS:
            batalla, _, _ = _batalla(nombre_clima)
            self.assertIn(nombre_clima, batalla.log[0],
                          f"El clima '{nombre_clima}' no aparece en el log inicial")


# ─────────────────────────────────────────────────────────────────────────────
# CA-4  El clima cambia según la zona
# ─────────────────────────────────────────────────────────────────────────────

class TestCambioClimaSegunZona(unittest.TestCase):
    """
    Verifica que Batalla acepta cualquier clima proveniente de zona.clima_base
    y que el objeto resultante refleja correctamente el clima elegido.
    """

    def test_batalla_refleja_clima_de_zona(self):
        from mapa import Mapa
        mapa = Mapa.crear_mapa_default()

        for nombre_zona, zona in mapa.zonas.items():
            cj = _criatura("Héroe", "Normal", hp=200, atk=10, velocidad=20)
            ce = _criatura("Villano", "Normal", hp=200, atk=1, velocidad=1,
                           precision=0.0)
            jugador = Jugador("Tester")
            jugador.agregar_criatura(cj)

            batalla = Batalla(jugador, ce, nombre_clima=zona.clima_base)
            self.assertEqual(batalla.condicion_climatica.nombre, zona.clima_base,
                             f"Zona '{nombre_zona}' no propagó su clima correctamente")

    def test_cambio_clima_entre_zonas_distintas(self):
        """Dos zonas con climas distintos producen batallas con climas distintos."""
        from mapa import Mapa
        mapa = Mapa.crear_mapa_default()

        zona_sol = mapa.obtener_zona("Pradera")   # Soleado
        zona_llu = mapa.obtener_zona("Lago")      # Lluvioso

        self.assertNotEqual(zona_sol.clima_base, zona_llu.clima_base,
                            "Las zonas de prueba deben tener climas distintos")

        def _b(zona):
            cj = _criatura("Héroe", "Normal", hp=200, atk=10, velocidad=20)
            ce = _criatura("Villano", "Normal", hp=200, atk=1, velocidad=1,
                           precision=0.0)
            j = Jugador("J")
            j.agregar_criatura(cj)
            return Batalla(j, ce, nombre_clima=zona.clima_base)

        b1 = _b(zona_sol)
        b2 = _b(zona_llu)
        self.assertNotEqual(b1.condicion_climatica.nombre,
                            b2.condicion_climatica.nombre)


# ─────────────────────────────────────────────────────────────────────────────
# CA-5  Retornos y excepciones documentados / validados
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentacionYExcepciones(unittest.TestCase):
    """
    Verifica que modificador_ataque posee docstring y que la clase lanza
    ValueError ante un nombre de clima inválido.
    """

    def test_modificador_ataque_tiene_docstring(self):
        self.assertIsNotNone(
            CondicionClimatica.modificador_ataque.__doc__,
            "modificador_ataque debe tener docstring"
        )

    def test_aplicar_dano_turno_tiene_docstring(self):
        self.assertIsNotNone(
            CondicionClimatica.aplicar_dano_turno.__doc__,
            "aplicar_dano_turno debe tener docstring"
        )

    def test_clima_invalido_lanza_value_error(self):
        with self.assertRaises(ValueError):
            CondicionClimatica("Marciano")

    def test_clima_invalido_mensaje_informativo(self):
        """El mensaje de error debe mencionar el clima inválido y los disponibles."""
        with self.assertRaises(ValueError) as ctx:
            CondicionClimatica("Galáctico")
        self.assertIn("Galáctico", str(ctx.exception))

    def test_todos_climas_validos_construyen_sin_error(self):
        for nombre in CLIMAS_VALIDOS:
            clima = CondicionClimatica(nombre)
            self.assertEqual(clima.nombre, nombre)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
