"""
condicion_climatica.py
======================
Define la clase CondicionClimatica, que representa el clima activo
en una zona durante el combate. Modifica el daño y la precisión
de las criaturas según su tipo elemental.

Climas disponibles: Soleado, Lluvioso, Tormentoso, Caluroso, Nevado
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from criatura import Criatura


# Datos de cada clima:
#   beneficia  → tipos que reciben +20% de ataque
#   perjudica  → tipos que reciben -10% de ataque
#   dano_turno → tipos que sufren daño fijo por turno {tipo: dano}
DATOS_CLIMA: dict[str, dict] = {
    "Soleado": {
        "beneficia": ["Fuego"],
        "perjudica": ["Agua"],
        "dano_turno": {},
    },
    "Lluvioso": {
        "beneficia": ["Agua"],
        "perjudica": ["Fuego"],
        "dano_turno": {"Fuego": 5},
    },
    "Tormentoso": {
        "beneficia": ["Rayo"],
        "perjudica": ["Tierra"],
        "dano_turno": {"Tierra": 3},
    },
    "Caluroso": {
        "beneficia": ["Fuego", "Tierra"],
        "perjudica": ["Agua"],
        "dano_turno": {},
    },
    "Nevado": {
        "beneficia": ["Agua"],
        "perjudica": ["Fuego", "Rayo"],
        "dano_turno": {"Fuego": 3, "Rayo": 2},
    },
}

CLIMAS_VALIDOS: list[str] = list(DATOS_CLIMA.keys())


class CondicionClimatica:
    """
    Representa el clima activo durante un combate en una zona.

    Modifica el combate de dos formas:
      1. Multiplicador de ataque según el tipo elemental de quien ataca.
      2. Daño por turno aplicado a criaturas de ciertos tipos.

    Atributos:
        nombre (str): Nombre del clima (ej. 'Lluvioso').
        beneficia (list[str]): Tipos que reciben +20% de ataque.
        perjudica (list[str]): Tipos que reciben -10% de ataque.
        dano_turno (dict[str, int]): Daño fijo por turno {tipo: daño}.

    Excepciones:
        ValueError: Si el nombre del clima no es válido.
    """

    def __init__(self, nombre: str) -> None:
        """
        Inicializa la condición climática.

        Parámetros:
            nombre (str): Nombre del clima. Debe pertenecer a CLIMAS_VALIDOS.

        Lanza:
            ValueError: Si el nombre no es un clima reconocido.
        """
        if nombre not in CLIMAS_VALIDOS:
            raise ValueError(
                f"Clima '{nombre}' no válido. Climas disponibles: {CLIMAS_VALIDOS}"
            )

        datos = DATOS_CLIMA[nombre]
        self.nombre: str = nombre
        self.beneficia: list[str] = datos["beneficia"]
        self.perjudica: list[str] = datos["perjudica"]
        self.dano_turno: dict[str, int] = datos["dano_turno"]

    def modificador_ataque(self, tipo: str) -> float:
        """
        Calcula el modificador de ataque para un tipo elemental dado.

        Parámetros:
            tipo (str): Tipo elemental del atacante (ej. 'Fuego').

        Retorna:
            float: 1.20 si el tipo es beneficiado, 0.90 si es perjudicado,
                   1.0 si el clima es neutro para ese tipo.
        """
        if tipo in self.beneficia:
            return 1.20
        if tipo in self.perjudica:
            return 0.90
        return 1.0

    def aplicar_dano_turno(self, criatura: "Criatura") -> int:
        """
        Aplica daño por turno a una criatura si el clima lo indica para su tipo.

        Parámetros:
            criatura (Criatura): La criatura sobre la que se aplica el efecto.

        Retorna:
            int: El daño aplicado (0 si el clima no afecta al tipo de la criatura).
        """
        dano = self.dano_turno.get(criatura.tipo.nombre, 0)
        if dano > 0:
            criatura.hp = max(0, criatura.hp - dano)
        return dano

    def descripcion(self) -> str:
        """
        Genera una descripción legible del clima y sus efectos.

        Retorna:
            str: Texto descriptivo del clima.
        """
        beneficiados = ", ".join(self.beneficia) if self.beneficia else "ninguno"
        perjudicados = ", ".join(self.perjudica) if self.perjudica else "ninguno"
        dano_str = (
            ", ".join(f"{t}: -{d} HP/turno" for t, d in self.dano_turno.items())
            if self.dano_turno
            else "ninguno"
        )
        return (
            f"Clima: {self.nombre} | "
            f"Potencia: {beneficiados} | "
            f"Debilita: {perjudicados} | "
            f"Daño/turno: {dano_str}"
        )

    def __repr__(self) -> str:
        return f"CondicionClimatica(nombre='{self.nombre}')"

    def __str__(self) -> str:
        return self.descripcion()
