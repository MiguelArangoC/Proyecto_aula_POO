"""
tipo.py
=======
Define la clase Tipo, que representa el tipo elemental de una criatura
y calcula los multiplicadores de daño entre tipos opuestos.

Tipos disponibles: Fuego, Agua, Tierra, Rayo, Normal
"""

from __future__ import annotations


# Tabla de multiplicadores: TABLA[atacante][defensor] -> float
# 1.5 = ventaja, 0.67 = desventaja (recíproco de 1.5), 1.0 = neutro
_TABLA_MULTIPLICADORES: dict[str, dict[str, float]] = {
    "Fuego": {
        "Fuego":  1.0,
        "Agua":   0.67,
        "Tierra": 1.5,
        "Rayo":   1.0,
        "Normal": 1.0,
    },
    "Agua": {
        "Fuego":  1.5,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   0.67,
        "Normal": 1.0,
    },
    "Tierra": {
        "Fuego":  0.67,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   1.5,
        "Normal": 1.0,
    },
    "Rayo": {
        "Fuego":  1.0,
        "Agua":   1.5,
        "Tierra": 0.67,
        "Rayo":   1.0,
        "Normal": 1.0,
    },
    "Normal": {
        "Fuego":  1.0,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   1.0,
        "Normal": 1.0,
    },
}

TIPOS_VALIDOS: list[str] = list(_TABLA_MULTIPLICADORES.keys())


class Tipo:
    """
    Representa el tipo elemental de una criatura y gestiona los
    multiplicadores de daño entre tipos.

    Atributos:
        nombre (str): Nombre del tipo elemental (ej. 'Fuego', 'Agua').

    Excepciones:
        ValueError: Si el nombre del tipo no es válido.
    """

    def __init__(self, nombre: str) -> None:
        """
        Inicializa el tipo elemental.

        Parámetros:
            nombre (str): Nombre del tipo. Debe pertenecer a TIPOS_VALIDOS.

        Lanza:
            ValueError: Si el nombre no es un tipo elemental reconocido.
        """
        if nombre not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo '{nombre}' no válido. Tipos disponibles: {TIPOS_VALIDOS}"
            )
        self.nombre: str = nombre

    def calcular_multiplicador(self, tipo_defensor: Tipo) -> float:
        """
        Calcula el multiplicador de daño al atacar a un defensor de un tipo dado.

        Parámetros:
            tipo_defensor (Tipo): El tipo elemental de la criatura defensora.

        Retorna:
            float: 1.5 si es ventajoso, 0.67 si es desventajoso, 1.0 si es neutro.

        Ejemplo:
            >>> fuego = Tipo("Fuego")
            >>> tierra = Tipo("Tierra")
            >>> fuego.calcular_multiplicador(tierra)
            1.5
        """
        return _TABLA_MULTIPLICADORES[self.nombre][tipo_defensor.nombre]

    def __repr__(self) -> str:
        return f"Tipo(nombre='{self.nombre}')"

    def __str__(self) -> str:
        return self.nombre
