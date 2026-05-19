"""
fragmento.py
============
Define la clase FragmentoEvolucion, ítem especial que se obtiene
explorando ciertas zonas del mapa y que permite evolucionar criaturas.

Cada criatura necesita un fragmento específico según su tipo elemental.
Los fragmentos se encuentran en zonas de mayor dificultad al explorar,
con una probabilidad reducida respecto a los encuentros de criaturas.

Relación zona → fragmento (definida también en mapa.py):
  Volcán        → Fragmento de Llama    (para Ignis)
  Lago          → Fragmento de Marea    (para Torrente)
  Cueva de Roca → Fragmento de Tierra   (para Rocafer)

Los fragmentos se almacenan en el inventario del jugador como cualquier
otro ítem, pero con es_consumible=True y es_captura=False.
"""

from __future__ import annotations


# ─────────────────────────────────────────
# CATÁLOGO DE FRAGMENTOS
# ─────────────────────────────────────────

CATALOGO_FRAGMENTOS: dict[str, dict] = {
    "Fragmento de Llama": {
        "descripcion": "Cristal incandescente hallado en el Volcán. Permite evolucionar a Ignis.",
        "tipo_criatura": "Fuego",
        "icono": "🔶",
        "zona_origen": "Volcán",
        "precio_gui": 0,
    },
    "Fragmento de Marea": {
        "descripcion": "Gema marina hallada en el Lago. Permite evolucionar a Torrente.",
        "tipo_criatura": "Agua",
        "icono": "🔷",
        "zona_origen": "Lago",
        "precio_gui": 0,
    },
    "Fragmento de Tierra": {
        "descripcion": "Núcleo pétreo hallado en la Cueva de Roca. Permite evolucionar a Rocafer.",
        "tipo_criatura": "Tierra",
        "icono": "🟫",
        "zona_origen": "Cueva de Roca",
        "precio_gui": 0,
    },
}

# Probabilidad de drop al explorar (independiente del encuentro de criatura)
PROBABILIDAD_DROP_FRAGMENTO: float = 0.25   # 25% al explorar la zona correcta


class FragmentoEvolucion:
    """
    Representa un fragmento de evolución obtenido explorando.

    No es una subclase de Item para mantener la separación de conceptos,
    pero el adaptador lo serializa como ítem del inventario al sincroni-
    zar con la GUI (tipo 'Material', no consumible, no captura).

    Atributos:
        nombre (str):        Nombre del fragmento.
        descripcion (str):   Texto para la GUI.
        tipo_criatura (str): Tipo elemental de la criatura que puede evolucionar con él.
        icono (str):         Emoji para la GUI.
        zona_origen (str):   Zona donde se puede encontrar.
    """

    def __init__(self, nombre: str) -> None:
        """
        Crea un fragmento desde el catálogo.

        Lanza:
            KeyError: Si el nombre no existe en CATALOGO_FRAGMENTOS.
        """
        if nombre not in CATALOGO_FRAGMENTOS:
            raise KeyError(
                f"Fragmento '{nombre}' no existe. "
                f"Disponibles: {list(CATALOGO_FRAGMENTOS.keys())}"
            )
        datos = CATALOGO_FRAGMENTOS[nombre]
        self.nombre: str = nombre
        self.descripcion: str = datos["descripcion"]
        self.tipo_criatura: str = datos["tipo_criatura"]
        self.icono: str = datos["icono"]
        self.zona_origen: str = datos["zona_origen"]

        # Atributos de compatibilidad con la interfaz de Item (para la GUI)
        self.efecto_positivo: dict = {}
        self.efecto_negativo: dict = {}
        self.es_consumible: bool = True   # Se consume al usarlo para evolucionar
        self.es_captura: bool = False
        self.es_fragmento: bool = True    # Marca especial para distinguir de Item

    def __repr__(self) -> str:
        return f"FragmentoEvolucion('{self.nombre}', tipo='{self.tipo_criatura}')"

    def __str__(self) -> str:
        return f"{self.icono} {self.nombre} — {self.descripcion}"