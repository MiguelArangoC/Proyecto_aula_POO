"""
fragmento.py
============
Define la clase FragmentoEvolucion, ítem especial que se obtiene
explorando ciertas zonas del mapa y que permite evolucionar criaturas.
"""

# Catálogo de fragmentos disponibles en el juego
CATALOGO_FRAGMENTOS = {
    "Fragmento de Llama": {
        "descripcion":   "Cristal incandescente hallado en el Volcán. Permite evolucionar a Ignis.",
        "tipo_criatura": "Fuego",
        "icono":         "🔶",
        "zona_origen":   "Volcán",
    },
    "Fragmento de Marea": {
        "descripcion":   "Gema marina hallada en el Lago. Permite evolucionar a Torrente.",
        "tipo_criatura": "Agua",
        "icono":         "🔷",
        "zona_origen":   "Lago",
    },
    "Fragmento de Tierra": {
        "descripcion":   "Núcleo pétreo hallado en la Cueva de Roca. Permite evolucionar a Rocafer.",
        "tipo_criatura": "Tierra",
        "icono":         "🟫",
        "zona_origen":   "Cueva de Roca",
    },
    "Fragmento de Trueno": {
        "descripcion":   "Cristal eléctrico hallado en la Cumbre Nevada. Permite evolucionar a Voltex.",
        "tipo_criatura": "Rayo",
        "icono":         "⚡",
        "zona_origen":   "Cumbre Nevada",
    },
    "Fragmento de Escarcha": {
        "descripcion":   "Gema helada hallada en la Cumbre Nevada. Permite evolucionar a Glacius.",
        "tipo_criatura": "Hielo",
        "icono":         "❄️",
        "zona_origen":   "Cumbre Nevada",
    },
}

# Probabilidad de encontrar un fragmento al explorar la zona correcta
PROBABILIDAD_DROP_FRAGMENTO = 0.25


class FragmentoEvolucion:
    """
    Representa un fragmento de evolución obtenido explorando.

    No es una subclase de Item para mantener la separación de conceptos,
    pero tiene los mismos atributos básicos para poder guardarse en el
    inventario del jugador junto a los ítems normales.
    """

    def __init__(self, nombre):
        if nombre not in CATALOGO_FRAGMENTOS:
            raise KeyError(
                f"Fragmento '{nombre}' no existe. "
                f"Disponibles: {list(CATALOGO_FRAGMENTOS.keys())}"
            )
        datos = CATALOGO_FRAGMENTOS[nombre]
        self.nombre          = nombre
        self.descripcion     = datos["descripcion"]
        self.tipo_criatura   = datos["tipo_criatura"]
        self.icono           = datos["icono"]
        self.zona_origen     = datos["zona_origen"]

        # Atributos de compatibilidad con la interfaz de Item (para la GUI)
        self.efecto_positivo = {}
        self.efecto_negativo = {}
        self.es_consumible   = True    # Se consume al usarlo para evolucionar
        self.es_captura      = False
        self.es_fragmento    = True    # Marca especial para distinguirlo de Item

    def __repr__(self):
        return f"FragmentoEvolucion('{self.nombre}', tipo='{self.tipo_criatura}')"

    def __str__(self):
        return f"{self.icono} {self.nombre} — {self.descripcion}"
