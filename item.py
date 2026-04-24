"""
item.py
=======
Define la clase Item, que representa objetos que el jugador puede
llevar en su inventario y equipar a sus criaturas para modificar
sus estadísticas en combate.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from criatura import Criatura


class Item:
    """
    Representa un ítem del inventario del jugador.

    Un ítem tiene dos efectos al ser equipado a una criatura:
      - efectoPositivo: beneficio que recibe la criatura (ej. +HP).
      - efectoNegativo: penalización que recibe la criatura (ej. -velocidad).

    Atributos:
        nombre (str): Nombre del ítem.
        descripcion (str): Breve descripción del ítem.
        efecto_positivo (dict[str, int]): Estadísticas que aumentan al equipar.
        efecto_negativo (dict[str, int]): Estadísticas que disminuyen al equipar.
        es_consumible (bool): True si el ítem se consume al usarse (ej. poción).
        es_captura (bool): True si el ítem sirve para capturar criaturas.
    """

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        efecto_positivo: dict[str, int],
        efecto_negativo: dict[str, int],
        es_consumible: bool = False,
        es_captura: bool = False,
    ) -> None:
        """
        Inicializa un ítem con sus efectos positivos y negativos.

        Parámetros:
            nombre (str): Nombre identificador del ítem.
            descripcion (str): Descripción breve del ítem.
            efecto_positivo (dict[str, int]): Claves son estadísticas (hp, atk,
                defensa, velocidad, precision) y valores son la cantidad de mejora.
            efecto_negativo (dict[str, int]): Claves son estadísticas y valores
                son la cantidad de penalización (positivos, se restarán).
            es_consumible (bool): Si True, desaparece del inventario al usarse.
            es_captura (bool): Si True, puede usarse para capturar criaturas.
        """
        self.nombre: str = nombre
        self.descripcion: str = descripcion
        self.efecto_positivo: dict[str, int] = efecto_positivo
        self.efecto_negativo: dict[str, int] = efecto_negativo
        self.es_consumible: bool = es_consumible
        self.es_captura: bool = es_captura

    def modificar_estadistica(self, criatura: "Criatura", revertir: bool = False) -> None:
        """
        Aplica o revierte los efectos del ítem sobre una criatura.

        Parámetros:
            criatura (Criatura): La criatura sobre la que se aplica el ítem.
            revertir (bool): Si True, revierte los efectos (para cambio de ítem).

        Retorna:
            None

        Lanza:
            AttributeError: Si la criatura no posee alguno de los atributos
                indicados en los efectos.
        """
        signo = -1 if revertir else 1

        for stat, valor in self.efecto_positivo.items():
            if hasattr(criatura, stat):
                setattr(criatura, stat, getattr(criatura, stat) + signo * valor)

        for stat, valor in self.efecto_negativo.items():
            if hasattr(criatura, stat):
                setattr(criatura, stat, getattr(criatura, stat) - signo * valor)

    def __repr__(self) -> str:
        return (
            f"Item(nombre='{self.nombre}', "
            f"efecto_positivo={self.efecto_positivo}, "
            f"efecto_negativo={self.efecto_negativo})"
        )

    def __str__(self) -> str:
        partes_pos = ", ".join(f"+{v} {k}" for k, v in self.efecto_positivo.items())
        partes_neg = ", ".join(f"-{v} {k}" for k, v in self.efecto_negativo.items())
        efectos = " | ".join(filter(None, [partes_pos, partes_neg]))
        return f"{self.nombre} ({efectos})"
