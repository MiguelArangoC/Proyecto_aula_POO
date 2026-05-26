"""
tipo.py
=======
Define la clase Tipo, que representa el tipo elemental de una criatura
y calcula los multiplicadores de daño entre tipos.

Tipos disponibles: Fuego, Agua, Tierra, Rayo, Hielo, Normal
"""

# Tabla de multiplicadores: _TABLA[atacante][defensor] -> numero
# 1.5 = ventaja, 0.67 = desventaja, 1.0 = neutro
_TABLA_MULTIPLICADORES = {
    "Fuego": {
        "Fuego":  1.0,
        "Agua":   0.67,
        "Tierra": 1.5,
        "Rayo":   1.0,
        "Hielo":  1.5,
        "Normal": 1.0,
    },
    "Agua": {
        "Fuego":  1.5,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   0.67,
        "Hielo":  0.67,
        "Normal": 1.0,
    },
    "Tierra": {
        "Fuego":  0.67,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   1.5,
        "Hielo":  0.67,
        "Normal": 1.0,
    },
    "Rayo": {
        "Fuego":  1.0,
        "Agua":   1.5,
        "Tierra": 0.67,
        "Rayo":   1.0,
        "Hielo":  1.0,
        "Normal": 1.0,
    },
    "Hielo": {
        "Fuego":  0.67,
        "Agua":   1.5,
        "Tierra": 1.5,
        "Rayo":   1.0,
        "Hielo":  1.0,
        "Normal": 1.0,
    },
    "Normal": {
        "Fuego":  1.0,
        "Agua":   1.0,
        "Tierra": 1.0,
        "Rayo":   1.0,
        "Hielo":  1.0,
        "Normal": 1.0,
    },
}

TIPOS_VALIDOS = list(_TABLA_MULTIPLICADORES.keys())


class Tipo:
    """
    Representa el tipo elemental de una criatura.
    Guarda el nombre y permite calcular el multiplicador de daño
    al atacar a otro tipo.
    """

    def __init__(self, nombre):
        if nombre not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo '{nombre}' no válido. Tipos disponibles: {TIPOS_VALIDOS}"
            )
        self.nombre = nombre

    def calcular_multiplicador(self, tipo_defensor):
        """
        Retorna el multiplicador de daño al atacar al tipo_defensor.
        1.5 si es ventajoso, 0.67 si es desventajoso, 1.0 si es neutro.
        """
        return _TABLA_MULTIPLICADORES[self.nombre][tipo_defensor.nombre]

    def __repr__(self):
        return f"Tipo(nombre='{self.nombre}')"

    def __str__(self):
        return self.nombre
