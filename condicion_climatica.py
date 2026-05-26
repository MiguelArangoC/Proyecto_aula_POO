"""
condicion_climatica.py
======================
Define la clase CondicionClimatica, que representa el clima activo
durante el combate. Modifica el daño y la precisión de las criaturas
según su tipo elemental.

Climas disponibles: Soleado, Lluvioso, Tormentoso, Caluroso, Nevado
"""

# Datos de cada clima:
#   beneficia  -> tipos que reciben +20% de ataque
#   perjudica  -> tipos que reciben -10% de ataque
#   dano_turno -> tipos que sufren daño fijo por turno {tipo: daño}
DATOS_CLIMA = {
    "Soleado": {
        "beneficia":  ["Fuego"],
        "perjudica":  ["Agua"],
        "dano_turno": {},
    },
    "Lluvioso": {
        "beneficia":  ["Agua"],
        "perjudica":  ["Fuego"],
        "dano_turno": {"Fuego": 5},
    },
    "Tormentoso": {
        "beneficia":  ["Rayo"],
        "perjudica":  ["Tierra"],
        "dano_turno": {"Tierra": 3},
    },
    "Caluroso": {
        "beneficia":  ["Fuego", "Tierra"],
        "perjudica":  ["Agua"],
        "dano_turno": {"Agua": 3},
    },
    "Nevado": {
        "beneficia":  ["Agua", "Hielo"],
        "perjudica":  ["Fuego", "Rayo"],
        "dano_turno": {"Fuego": 3, "Rayo": 2},
    },
}

CLIMAS_VALIDOS = list(DATOS_CLIMA.keys())


class CondicionClimatica:
    """
    Representa el clima activo durante un combate en una zona.

    Modifica el combate de dos formas:
      1. Multiplicador de ataque según el tipo elemental del atacante.
      2. Daño fijo por turno a criaturas de ciertos tipos.
    """

    def __init__(self, nombre):
        if nombre not in CLIMAS_VALIDOS:
            raise ValueError(
                f"Clima '{nombre}' no válido. Climas disponibles: {CLIMAS_VALIDOS}"
            )
        datos = DATOS_CLIMA[nombre]
        self.nombre     = nombre
        self.beneficia  = datos["beneficia"]
        self.perjudica  = datos["perjudica"]
        self.dano_turno = datos["dano_turno"]

    def modificador_ataque(self, tipo):
        """
        Retorna el multiplicador de ataque para un tipo elemental.
        1.20 si el tipo es beneficiado, 0.90 si es perjudicado, 1.0 si es neutro.
        """
        if tipo in self.beneficia:
            return 1.20
        if tipo in self.perjudica:
            return 0.90
        return 1.0

    def aplicar_dano_turno(self, criatura):
        """
        Aplica daño por turno a una criatura si el clima lo indica.
        Retorna el daño aplicado (0 si el clima no afecta ese tipo).
        """
        dano = self.dano_turno.get(criatura.tipo.nombre, 0)
        if dano > 0:
            criatura.hp = max(0, criatura.hp - dano)
        return dano

    def descripcion(self):
        """Genera una descripción legible del clima y sus efectos."""
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

    def __repr__(self):
        return f"CondicionClimatica(nombre='{self.nombre}')"

    def __str__(self):
        return self.descripcion()
