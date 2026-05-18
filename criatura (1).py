"""
criatura.py
===========
Define la clase Criatura, que representa a las entidades que el jugador
puede capturar y usar en combate. Incluye todos los atributos de combate
(HP, ataque, defensa, velocidad, precisión), nivel y experiencia.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from tipo import Tipo

if TYPE_CHECKING:
    from item import Item


class Criatura:
    """
    Representa una criatura del juego con atributos de combate y progresión.

    Atributos:
        nombre (str): Nombre de la criatura.
        tipo (Tipo): Tipo elemental de la criatura.
        hp (int): Puntos de vida actuales.
        hp_max (int): Puntos de vida máximos.
        atk (int): Estadística de ataque base.
        defensa (int): Estadística de defensa (reduce el daño recibido).
        velocidad (int): Determina el orden de ataque en combate.
        precision (float): Probabilidad base de acertar un ataque (0.0 – 1.0).
        nivel (int): Nivel actual de la criatura (empieza en 1).
        experiencia (int): Experiencia acumulada en el nivel actual.
        xp_siguiente (int): Experiencia necesaria para subir al siguiente nivel.
        item_equipado (Optional[Item]): Ítem actualmente equipado (None si vacío).
    """

    XP_BASE: int = 100        # XP necesaria para pasar del nivel 1 al 2
    XP_FACTOR: float = 1.5    # Factor multiplicador por nivel

    def __init__(
        self,
        nombre: str,
        tipo: str,
        hp: int,
        atk: int,
        defensa: int = 10,
        velocidad: int = 10,
        precision: float = 0.90,
        nivel: int = 1,
    ) -> None:
        """
        Inicializa una criatura con sus estadísticas base.

        Parámetros:
            nombre (str): Nombre de la criatura.
            tipo (str): Nombre del tipo elemental (ej. 'Fuego').
            hp (int): Puntos de vida iniciales y máximos.
            atk (int): Poder de ataque base.
            defensa (int): Valor de defensa base. Por defecto 10.
            velocidad (int): Valor de velocidad base. Por defecto 10.
            precision (float): Probabilidad de acierto (0.0–1.0). Por defecto 0.90.
            nivel (int): Nivel inicial. Por defecto 1.

        Lanza:
            ValueError: Si hp, atk o defensa son menores o iguales a 0.
            ValueError: Si precision no está en el rango [0.0, 1.0].
        """
        if hp <= 0 or atk <= 0 or defensa <= 0:
            raise ValueError("hp, atk y defensa deben ser mayores que 0.")
        if not (0.0 <= precision <= 1.0):
            raise ValueError("precision debe estar entre 0.0 y 1.0.")

        self.nombre: str = nombre
        self.tipo: Tipo = Tipo(tipo)
        self.hp: int = hp
        self.hp_max: int = hp
        self.atk: int = atk
        self.defensa: int = defensa
        self.velocidad: int = velocidad
        self.precision: float = precision
        self.nivel: int = nivel
        self.experiencia: int = 0
        self.xp_siguiente: int = int(self.XP_BASE * (self.XP_FACTOR ** (nivel - 1)))
        self.item_equipado: Optional["Item"] = None

    # ─────────────────────────────────────────
    # ESTADO
    # ─────────────────────────────────────────

    def esta_debilitada(self) -> bool:
        """
        Indica si la criatura está fuera de combate (HP ≤ 0).

        Retorna:
            bool: True si HP es 0 o menor.
        """
        return self.hp <= 0

    # ─────────────────────────────────────────
    # PROGRESIÓN
    # ─────────────────────────────────────────

    def ganar_experiencia(self, xp: int) -> bool:
        """
        Agrega experiencia a la criatura y sube de nivel tantas veces como
        corresponda si la XP ganada supera uno o más umbrales.

        Parámetros:
            xp (int): Cantidad de experiencia ganada (debe ser > 0).

        Retorna:
            bool: True si la criatura subió al menos un nivel, False si no.

        Lanza:
            ValueError: Si xp es menor o igual a 0.
        """
        if xp <= 0:
            raise ValueError("La experiencia ganada debe ser mayor que 0.")

        self.experiencia += xp
        subio = False
        while self.experiencia >= self.xp_siguiente:
            self._subir_nivel()
            subio = True
        return subio

    def _subir_nivel(self) -> None:
        """
        Incrementa el nivel de la criatura y escala sus estadísticas.
        Descuenta la XP del umbral actual antes de recalcularlo.
        Método interno; usar ganar_experiencia() desde el exterior.

        Retorna:
            None
        """
        self.experiencia -= self.xp_siguiente
        self.nivel += 1
        self.xp_siguiente = int(self.XP_BASE * (self.XP_FACTOR ** (self.nivel - 1)))

        # Escala de estadísticas al subir de nivel
        self.hp_max = int(self.hp_max * 1.10)
        self.hp = self.hp_max        # restaura HP al subir de nivel
        self.atk = int(self.atk * 1.08)
        self.defensa = int(self.defensa * 1.05)
        self.velocidad = int(self.velocidad * 1.05)

    # ─────────────────────────────────────────
    # REPRESENTACIÓN
    # ─────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Criatura(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"hp={self.hp}/{self.hp_max}, nivel={self.nivel})"
        )

    def __str__(self) -> str:
        item_str = f" [{self.item_equipado.nombre}]" if self.item_equipado else ""
        return (
            f"{self.nombre} (Nv.{self.nivel} | {self.tipo}){item_str} "
            f"HP:{self.hp}/{self.hp_max} ATK:{self.atk} DEF:{self.defensa} VEL:{self.velocidad}"
        )
