"""
item.py
=======
Define la clase Item, que representa objetos que el jugador puede
llevar en su inventario y equipar a sus criaturas para modificar
sus estadísticas en combate.
"""


class Item:
    """
    Representa un ítem del inventario del jugador.

    Un ítem tiene dos efectos al ser equipado a una criatura:
      - efecto_positivo: beneficio que recibe la criatura (ej. +HP).
      - efecto_negativo: penalización que recibe la criatura (ej. -velocidad).
    """

    def __init__(
        self,
        nombre,
        descripcion,
        efecto_positivo,
        efecto_negativo,
        es_consumible=False,
        es_captura=False,
    ):
        self.nombre          = nombre
        self.descripcion     = descripcion
        self.efecto_positivo = efecto_positivo   # dict {stat: cantidad}
        self.efecto_negativo = efecto_negativo   # dict {stat: cantidad}
        self.es_consumible   = es_consumible
        self.es_captura      = es_captura

    def modificar_estadistica(self, criatura, revertir=False):
        """
        Aplica o revierte los efectos del ítem sobre una criatura.

        Si revertir=False aplica los efectos (al equipar).
        Si revertir=True los deshace (al cambiar de ítem).
        """
        # Determina si sumamos o restamos
        if revertir:
            signo = -1
        else:
            signo = 1

        # Aplicar efectos positivos
        for stat, valor in self.efecto_positivo.items():
            if stat == "hp":
                criatura.hp += signo * valor
            elif stat == "atk":
                criatura.atk += signo * valor
            elif stat == "defensa":
                criatura.defensa += signo * valor
            elif stat == "velocidad":
                criatura.velocidad += signo * valor
            elif stat == "precision":
                criatura.precision += signo * valor

        # Aplicar efectos negativos
        for stat, valor in self.efecto_negativo.items():
            if stat == "hp":
                criatura.hp -= signo * valor
            elif stat == "atk":
                criatura.atk -= signo * valor
            elif stat == "defensa":
                criatura.defensa -= signo * valor
            elif stat == "velocidad":
                criatura.velocidad -= signo * valor
            elif stat == "precision":
                criatura.precision -= signo * valor

    def __repr__(self):
        return (
            f"Item(nombre='{self.nombre}', "
            f"efecto_positivo={self.efecto_positivo}, "
            f"efecto_negativo={self.efecto_negativo})"
        )

    def __str__(self):
        partes_pos = ", ".join(f"+{v} {k}" for k, v in self.efecto_positivo.items())
        partes_neg = ", ".join(f"-{v} {k}" for k, v in self.efecto_negativo.items())
        if partes_pos and partes_neg:
            efectos = partes_pos + " | " + partes_neg
        elif partes_pos:
            efectos = partes_pos
        else:
            efectos = partes_neg
        return f"{self.nombre} ({efectos})"
