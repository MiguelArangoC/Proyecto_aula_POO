"""
tipo.py
=======
Define la clase Tipo, que representa el tipo elemental de una criatura
y calcula los multiplicadores de daño entre tipos opuestos.

Tipos base:   Fuego, Agua, Tierra, Rayo, Hielo, Normal
Tipos de cruza (híbridos):
    Vapor         (Fuego × Agua)
    Magma         (Fuego × Tierra)
    Choque Térmico (Fuego × Hielo)
    Plasma        (Fuego × Rayo)
    Pantano       (Agua × Tierra)
    Escarcha      (Agua × Hielo)
    Tormenta      (Agua × Rayo)
    Cristal       (Tierra × Hielo)
    Metal         (Tierra × Rayo)
    Aurora        (Hielo × Rayo)

Multiplicadores:
    1.5  → ventaja clara (interacción elemental directa)
    1.3  → ventaja moderada (herencia parcial de tipo híbrido)
    1.0  → neutro
    0.8  → desventaja moderada (herencia parcial)
    0.67 → desventaja clara (≈ recíproco de 1.5)
"""

from __future__ import annotations


# Tabla de multiplicadores: TABLA[atacante][defensor] → float
_TABLA_MULTIPLICADORES: dict[str, dict[str, float]] = {

    # ══════════════════════════════════════════════════════════════════════════
    # TIPOS BASE
    # ══════════════════════════════════════════════════════════════════════════

    "Fuego": {
        # Base
        "Fuego": 1.0,  "Agua": 0.67, "Tierra": 1.5,  "Rayo": 1.0,  "Hielo": 1.5,  "Normal": 1.0,
        # Híbridos: fuerte vs tipos con Hielo/Tierra, débil frente a los acuáticos
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.5, "Escarcha": 1.5, "Tormenta": 1.0, "Cristal": 1.3, "Metal": 1.5, "Aurora": 1.3,
    },
    "Agua": {
        # Base
        "Fuego": 1.5,  "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 0.67, "Hielo": 0.67, "Normal": 1.0,
        # Híbridos: fuerte vs tipos con Fuego/Tierra, débil vs Plasma (rayo)
        "Vapor": 1.3,  "Magma": 1.5,  "Choque Térmico": 1.0,  "Plasma": 0.67,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.3, "Aurora": 1.0,
    },
    "Tierra": {
        # Base
        "Fuego": 0.67, "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.5,  "Hielo": 0.67, "Normal": 1.0,
        # Híbridos: fuerte vs Plasma (rayo), débil vs Tormenta/Aurora (rayo)
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.5,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 0.67, "Cristal": 1.0, "Metal": 1.0, "Aurora": 0.67,
    },
    "Rayo": {
        # Base
        "Fuego": 1.0,  "Agua": 1.5,  "Tierra": 0.67, "Rayo": 1.0,  "Hielo": 1.0,  "Normal": 1.0,
        # Híbridos: fuerte vs acuáticos, débil vs Metal/Cristal (tierra aísla)
        "Vapor": 1.3,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.3, "Escarcha": 1.5, "Tormenta": 1.0, "Cristal": 0.67, "Metal": 0.67, "Aurora": 1.0,
    },
    "Hielo": {
        # Base
        "Fuego": 0.67, "Agua": 1.5,  "Tierra": 1.5,  "Rayo": 1.0,  "Hielo": 1.0,  "Normal": 1.0,
        # Híbridos: fuerte vs acuosos/tierra, débil vs Magma/Plasma (fuego)
        "Vapor": 1.0,  "Magma": 0.67, "Choque Térmico": 1.0,  "Plasma": 0.67,
        "Pantano": 1.5, "Escarcha": 1.0, "Tormenta": 1.5, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },
    "Normal": {
        # Base
        "Fuego": 1.0,  "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.0,  "Hielo": 1.0,  "Normal": 1.0,
        # Híbridos: siempre neutro
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ══════════════════════════════════════════════════════════════════════════
    # TIPOS HÍBRIDOS (cruzas)
    # Regla: híbrido vs híbrido = 1.0 (neutro)
    # Interacciones vs base: herencia ponderada de ambos padres elementales.
    # ══════════════════════════════════════════════════════════════════════════

    # ── Vapor (Fuego × Agua) ──────────────────────────────────────────────────
    # Hereda la ventaja de Fuego sobre Tierra (moderada), penalizado por Rayo
    "Vapor": {
        "Fuego": 1.0,  "Agua": 1.0,  "Tierra": 1.3,  "Rayo": 0.8,  "Hielo": 1.0,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Magma (Fuego × Tierra) ────────────────────────────────────────────────
    # Muy fuerte vs Hielo (ambos padres tienen ventaja), débil vs Agua
    "Magma": {
        "Fuego": 0.8,  "Agua": 0.67, "Tierra": 1.0,  "Rayo": 1.0,  "Hielo": 1.5,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.3, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Choque Térmico (Fuego × Hielo) ────────────────────────────────────────
    # Los elementos se anulan: ventajas de Fuego vs Hielo = desventajas de Hielo vs Fuego.
    # Resultado: tipo sorpresa, ventaja moderada vs Normal (inestabilidad térmica)
    "Choque Térmico": {
        "Fuego": 1.0,  "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.0,  "Hielo": 1.0,  "Normal": 1.3,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Plasma (Fuego × Rayo) ─────────────────────────────────────────────────
    # Muy fuerte vs Agua (ambos), débil vs Tierra (tierra apaga rayo y sofoca fuego)
    "Plasma": {
        "Fuego": 1.0,  "Agua": 1.5,  "Tierra": 0.67, "Rayo": 1.0,  "Hielo": 1.3,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Pantano (Agua × Tierra) ───────────────────────────────────────────────
    # Fuerte vs Fuego (agua apaga), débil vs Hielo (congela el lodo)
    "Pantano": {
        "Fuego": 1.5,  "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.0,  "Hielo": 0.67, "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Escarcha (Agua × Hielo) ───────────────────────────────────────────────
    # Muy fuerte vs Fuego (ambos padres), débil vs Rayo (electricidad → agua conductora)
    "Escarcha": {
        "Fuego": 1.5,  "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 0.67, "Hielo": 1.0,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Tormenta (Agua × Rayo) ────────────────────────────────────────────────
    # Fuerte vs Tierra (rayo) y Fuego (agua), débil vs Hielo (congela la tormenta)
    "Tormenta": {
        "Fuego": 1.3,  "Agua": 1.0,  "Tierra": 1.5,  "Rayo": 1.0,  "Hielo": 0.67, "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Cristal (Tierra × Hielo) ──────────────────────────────────────────────
    # Fuerte vs Rayo (tierra bloquea), débil vs Fuego (derrite el cristal)
    "Cristal": {
        "Fuego": 0.67, "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.5,  "Hielo": 1.0,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Metal (Tierra × Rayo) ─────────────────────────────────────────────────
    # Ventaja moderada vs Hielo (conduce energía), débil vs Fuego (funde el metal)
    "Metal": {
        "Fuego": 0.67, "Agua": 1.0,  "Tierra": 1.0,  "Rayo": 1.0,  "Hielo": 1.3,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },

    # ── Aurora (Hielo × Rayo) ─────────────────────────────────────────────────
    # Fuerte vs Tierra (rayo), ventaja moderada vs Agua (hielo), débil vs Fuego
    "Aurora": {
        "Fuego": 0.67, "Agua": 1.3,  "Tierra": 1.5,  "Rayo": 1.0,  "Hielo": 1.0,  "Normal": 1.0,
        "Vapor": 1.0,  "Magma": 1.0,  "Choque Térmico": 1.0,  "Plasma": 1.0,
        "Pantano": 1.0, "Escarcha": 1.0, "Tormenta": 1.0, "Cristal": 1.0, "Metal": 1.0, "Aurora": 1.0,
    },
}

TIPOS_VALIDOS: list[str] = list(_TABLA_MULTIPLICADORES.keys())


class Tipo:
    """
    Representa el tipo elemental de una criatura y gestiona los
    multiplicadores de daño entre tipos.

    Soporta tanto tipos base (Fuego, Agua, Tierra, Rayo, Hielo, Normal)
    como tipos híbridos de cruza (Vapor, Magma, Choque Térmico, Plasma,
    Pantano, Escarcha, Tormenta, Cristal, Metal, Aurora).

    Atributos:
        nombre (str): Nombre del tipo elemental.

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
            float: Multiplicador de daño (1.5, 1.3, 1.0, 0.8 o 0.67).

        Ejemplo:
            >>> fuego = Tipo("Fuego")
            >>> tierra = Tipo("Tierra")
            >>> fuego.calcular_multiplicador(tierra)
            1.5
            >>> plasma = Tipo("Plasma")
            >>> agua = Tipo("Agua")
            >>> plasma.calcular_multiplicador(agua)
            1.5
        """
        return _TABLA_MULTIPLICADORES[self.nombre][tipo_defensor.nombre]

    def __repr__(self) -> str:
        return f"Tipo(nombre='{self.nombre}')"

    def __str__(self) -> str:
        return self.nombre
