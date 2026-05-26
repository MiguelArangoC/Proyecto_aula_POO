"""
cruza.py
========
Sistema de cruzamiento entre criaturas del juego.

Tabla de cruzas (tipo A x tipo B -> tipo resultado):
  Fuego  x Agua   -> Vapor
  Fuego  x Tierra -> Magma
  Fuego  x Hielo  -> Choque Termico
  Fuego  x Rayo   -> Plasma
  Agua   x Tierra -> Pantano
  Agua   x Hielo  -> Escarcha
  Agua   x Rayo   -> Tormenta
  Tierra x Hielo  -> Cristal
  Tierra x Rayo   -> Metal
  Hielo  x Rayo   -> Aurora

Mutaciones raras (5% de probabilidad):
  Plasma  -> Plasma Alfa
  Cristal -> Cristal Corrupto
  (más en TABLA_MUTACIONES)
"""

import random


# ─────────────────────────────────────────
# TABLA DE CRUZAS
# Usamos frozenset como clave porque la cruza A x B es igual a B x A.
# frozenset({"Fuego", "Agua"}) es igual a frozenset({"Agua", "Fuego"})
# ─────────────────────────────────────────

TABLA_CRUZAS = {
    frozenset({"Fuego", "Agua"}): {
        "tipo_resultado":       "Vapor",
        "nombre_base":          "Vapora",
        "icono":                "💨",
        "color":                "#B0C4DE",
        "afinidad":             "evasion_fisica",
        "desc_afinidad":        "Envuelta en vapor, evade un 30% de los ataques físicos recibidos.",
        "escala_hp":   1.00, "escala_atk": 1.05, "escala_def": 1.00, "escala_vel": 1.15,
        "habilidades_exclusivas": ["Cortina de Vapor", "Burbuja Escaldante"],
    },
    frozenset({"Fuego", "Tierra"}): {
        "tipo_resultado":       "Magma",
        "nombre_base":          "Magmor",
        "icono":                "🌋",
        "color":                "#CC4400",
        "afinidad":             "resistencia_fuego",
        "desc_afinidad":        "Cuerpo de roca fundida: absorbe el 50% del daño de tipo Fuego.",
        "escala_hp":   1.10, "escala_atk": 1.10, "escala_def": 1.15, "escala_vel": 0.90,
        "habilidades_exclusivas": ["Oleada de Lava", "Coraza Ígnea"],
    },
    frozenset({"Fuego", "Hielo"}): {
        "tipo_resultado":       "Choque Térmico",
        "nombre_base":          "Termox",
        "icono":                "❄🔥",
        "color":                "#8A2BE2",
        "afinidad":             "confusion_termica",
        "desc_afinidad":        "Sus ataques tienen 25% de probabilidad de confundir al objetivo.",
        "escala_hp":   1.05, "escala_atk": 1.20, "escala_def": 0.95, "escala_vel": 1.05,
        "habilidades_exclusivas": ["Pulso Dual", "Fractura Térmica"],
    },
    frozenset({"Fuego", "Rayo"}): {
        "tipo_resultado":       "Plasma",
        "nombre_base":          "Plasmar",
        "icono":                "⚡🔥",
        "color":                "#FFD700",
        "afinidad":             "sobrecarga",
        "desc_afinidad":        "Cada 3 turnos libera una descarga automática de 15 de daño fijo.",
        "escala_hp":   0.95, "escala_atk": 1.25, "escala_def": 0.90, "escala_vel": 1.20,
        "habilidades_exclusivas": ["Arco de Plasma", "Nova Solar"],
    },
    frozenset({"Agua", "Tierra"}): {
        "tipo_resultado":       "Pantano",
        "nombre_base":          "Cenagar",
        "icono":                "🟫💧",
        "color":                "#556B2F",
        "afinidad":             "ralentizar",
        "desc_afinidad":        "Sus ataques reducen la velocidad del enemigo en 3 puntos durante 2 turnos.",
        "escala_hp":   1.12, "escala_atk": 1.00, "escala_def": 1.10, "escala_vel": 0.95,
        "habilidades_exclusivas": ["Trampa de Lodo", "Absorción Pantanosa"],
    },
    frozenset({"Agua", "Hielo"}): {
        "tipo_resultado":       "Escarcha",
        "nombre_base":          "Frostyn",
        "icono":                "🧊",
        "color":                "#ADD8E6",
        "afinidad":             "congelacion",
        "desc_afinidad":        "15% de probabilidad de congelar al objetivo por 1 turno.",
        "escala_hp":   1.05, "escala_atk": 1.05, "escala_def": 1.10, "escala_vel": 1.00,
        "habilidades_exclusivas": ["Aliento Glacial", "Tormenta de Agujas"],
    },
    frozenset({"Agua", "Rayo"}): {
        "tipo_resultado":       "Tormenta",
        "nombre_base":          "Tempest",
        "icono":                "⛈",
        "color":                "#4682B4",
        "afinidad":             "cadena_electrica",
        "desc_afinidad":        "Al atacar, 20% de que el daño se encadene al siguiente turno.",
        "escala_hp":   1.00, "escala_atk": 1.15, "escala_def": 1.00, "escala_vel": 1.10,
        "habilidades_exclusivas": ["Rayo Torrencial", "Ojo del Huracán"],
    },
    frozenset({"Tierra", "Hielo"}): {
        "tipo_resultado":       "Cristal",
        "nombre_base":          "Crystar",
        "icono":                "💎",
        "color":                "#E0FFFF",
        "afinidad":             "reflejo_daño",
        "desc_afinidad":        "Refleja el 20% del daño físico recibido de vuelta al atacante.",
        "escala_hp":   1.08, "escala_atk": 1.00, "escala_def": 1.20, "escala_vel": 0.95,
        "habilidades_exclusivas": ["Fragmento Cortante", "Armadura Cristalina"],
    },
    frozenset({"Tierra", "Rayo"}): {
        "tipo_resultado":       "Metal",
        "nombre_base":          "Ferron",
        "icono":                "⚙️",
        "color":                "#A9A9A9",
        "afinidad":             "blindaje_electrico",
        "desc_afinidad":        "Inmune a reducción de velocidad. DEF bloquea 10% extra de daño.",
        "escala_hp":   1.10, "escala_atk": 1.05, "escala_def": 1.25, "escala_vel": 0.90,
        "habilidades_exclusivas": ["Carga Metálica", "Escudo Conductor"],
    },
    frozenset({"Hielo", "Rayo"}): {
        "tipo_resultado":       "Aurora",
        "nombre_base":          "Aurorix",
        "icono":                "🌌",
        "color":                "#DA70D6",
        "afinidad":             "aura_prismatica",
        "desc_afinidad":        "Al inicio del combate otorga +10% ATK a todo el equipo por 3 turnos.",
        "escala_hp":   1.02, "escala_atk": 1.12, "escala_def": 1.05, "escala_vel": 1.12,
        "habilidades_exclusivas": ["Destello Boreal", "Prisma Cósmico"],
    },
}

# ─────────────────────────────────────────
# MUTACIONES RARAS
# ─────────────────────────────────────────

PROBABILIDAD_MUTACION = 0.05   # 5%

TABLA_MUTACIONES = {
    "Plasma": {
        "nombre_mutacion": "Plasma Alfa",
        "icono":           "⚡⚡",
        "color":           "#FF4500",
        "bonus_atk":       15,
        "bonus_vel":       10,
        "bonus_desc":      "ATK +15, VEL +10, habilidad exclusiva Overload.",
        "habilidad_extra": "Overload",
    },
    "Cristal": {
        "nombre_mutacion": "Cristal Corrupto",
        "icono":           "🖤💎",
        "color":           "#9400D3",
        "bonus_atk":       12,
        "bonus_def":       8,
        "bonus_desc":      "ATK +12, DEF +8, reflejo de daño sube al 35%.",
        "habilidad_extra": "Espejo Oscuro",
    },
    "Aurora": {
        "nombre_mutacion": "Aurora Caótica",
        "icono":           "🌌💥",
        "color":           "#FF1493",
        "bonus_atk":       10,
        "bonus_vel":       8,
        "bonus_hp":        20,
        "bonus_desc":      "HP +20, ATK +10, VEL +8. Aura prisma activa desde el turno 1.",
        "habilidad_extra": "Caos Estelar",
    },
    "Tormenta": {
        "nombre_mutacion": "Tormenta Perfecta",
        "icono":           "⛈⚡",
        "color":           "#00BFFF",
        "bonus_atk":       18,
        "bonus_desc":      "ATK +18. La cadena eléctrica activa al 40%.",
        "habilidad_extra": "Tifón Eléctrico",
    },
    "Magma": {
        "nombre_mutacion": "Magma Primordial",
        "icono":           "🌋🔥",
        "color":           "#8B0000",
        "bonus_atk":       10,
        "bonus_def":       12,
        "bonus_hp":        15,
        "bonus_desc":      "HP +15, ATK +10, DEF +12. Absorción de fuego sube al 75%.",
        "habilidad_extra": "Núcleo Fundido",
    },
    "Escarcha": {
        "nombre_mutacion": "Escarcha Eternal",
        "icono":           "🧊❄",
        "color":           "#00CED1",
        "bonus_atk":       8,
        "bonus_def":       10,
        "bonus_vel":       5,
        "bonus_desc":      "ATK +8, DEF +10, VEL +5. Congelación al 30%.",
        "habilidad_extra": "Blizzard Eterno",
    },
}

# ─────────────────────────────────────────
# HABILIDADES EXCLUSIVAS DE CRUZA
# ─────────────────────────────────────────

HABILIDADES_CRUZA = {
    "Cortina de Vapor":    {"tipo": "esquivar", "costo_mp": 18, "potencia": 0.0,  "desc": "Se oculta en vapor. -50% de acierto enemigo este turno.",         "icono": "💨"},
    "Burbuja Escaldante":  {"tipo": "especial", "costo_mp": 22, "potencia": 1.8,  "desc": "Burbuja de agua hirviente. Penetra defensa.",                      "icono": "💧"},
    "Oleada de Lava":      {"tipo": "ataque",   "costo_mp": 15, "potencia": 1.6,  "desc": "Ola de magma ardiente.",                                           "icono": "🌋"},
    "Coraza Ígnea":        {"tipo": "soporte",  "costo_mp": 20, "potencia": 0.30, "desc": "Endurece el cuerpo con roca fundida. Recupera 30% HP.",             "icono": "🛡"},
    "Pulso Dual":          {"tipo": "especial", "costo_mp": 25, "potencia": 2.0,  "desc": "Disparo de energía fría y caliente. Ignora DEF.",                  "icono": "❄🔥"},
    "Fractura Térmica":    {"tipo": "ataque",   "costo_mp": 18, "potencia": 1.7,  "desc": "Choque de temperaturas extremas.",                                 "icono": "💥"},
    "Arco de Plasma":      {"tipo": "ataque",   "costo_mp": 20, "potencia": 1.7,  "desc": "Disparo de energía plasmática.",                                   "icono": "⚡🔥"},
    "Nova Solar":          {"tipo": "especial", "costo_mp": 38, "potencia": 2.8,  "desc": "Explosión de plasma solar. Máximo poder.",                         "icono": "☀"},
    "Trampa de Lodo":      {"tipo": "ataque",   "costo_mp": 15, "potencia": 1.4,  "desc": "Atrapa al enemigo en lodo espeso.",                                "icono": "🟫"},
    "Absorción Pantanosa": {"tipo": "soporte",  "costo_mp": 22, "potencia": 0.35, "desc": "Absorbe energía del entorno. Recupera 35% HP.",                    "icono": "💚"},
    "Aliento Glacial":     {"tipo": "ataque",   "costo_mp": 15, "potencia": 1.5,  "desc": "Soplo helado de alta precisión.",                                  "icono": "🧊"},
    "Tormenta de Agujas":  {"tipo": "especial", "costo_mp": 25, "potencia": 2.0,  "desc": "Lluvia de agujas de hielo. Penetra defensa.",                      "icono": "❄"},
    "Rayo Torrencial":     {"tipo": "especial", "costo_mp": 28, "potencia": 2.1,  "desc": "Relámpago combinado con agua. Altísimo daño.",                     "icono": "⛈"},
    "Ojo del Huracán":     {"tipo": "esquivar", "costo_mp": 22, "potencia": 0.0,  "desc": "Centro del huracán. -50% de acierto enemigo.",                     "icono": "🌀"},
    "Fragmento Cortante":  {"tipo": "ataque",   "costo_mp": 15, "potencia": 1.5,  "desc": "Lanza fragmentos de cristal afilados.",                            "icono": "💎"},
    "Armadura Cristalina": {"tipo": "soporte",  "costo_mp": 20, "potencia": 0.25, "desc": "Crea una capa cristalina. Recupera 25% HP.",                       "icono": "🛡"},
    "Carga Metálica":      {"tipo": "especial", "costo_mp": 25, "potencia": 2.0,  "desc": "Embestida de metal puro. Ignora parte de la DEF.",                 "icono": "⚙️"},
    "Escudo Conductor":    {"tipo": "soporte",  "costo_mp": 18, "potencia": 0.30, "desc": "Crea un campo conductor defensivo. Recupera 30% HP.",              "icono": "⚡"},
    "Destello Boreal":     {"tipo": "ataque",   "costo_mp": 18, "potencia": 1.6,  "desc": "Destello de luz boreal que deslumbra.",                            "icono": "🌌"},
    "Prisma Cósmico":      {"tipo": "especial", "costo_mp": 35, "potencia": 2.5,  "desc": "Rayo prismático cósmico. Ignora DEF.",                             "icono": "✨"},
    "Overload":            {"tipo": "especial", "costo_mp": 45, "potencia": 3.0,  "desc": "Sobrecarga total. Daño devastador. Solo en mutación Plasma Alfa.",  "icono": "⚡⚡"},
    "Espejo Oscuro":       {"tipo": "especial", "costo_mp": 40, "potencia": 2.7,  "desc": "Reflejo oscuro que canaliza el daño recibido.",                    "icono": "🖤"},
    "Caos Estelar":        {"tipo": "especial", "costo_mp": 42, "potencia": 2.8,  "desc": "Explosión de energía estelar caótica.",                            "icono": "🌌💥"},
    "Tifón Eléctrico":     {"tipo": "especial", "costo_mp": 40, "potencia": 2.9,  "desc": "Tifón de energía eléctrica. Daño en cadena.",                      "icono": "⛈⚡"},
    "Núcleo Fundido":      {"tipo": "especial", "costo_mp": 38, "potencia": 2.6,  "desc": "Libera el núcleo de magma interno.",                               "icono": "🌋🔥"},
    "Blizzard Eterno":     {"tipo": "especial", "costo_mp": 40, "potencia": 2.7,  "desc": "Ventisca eterna que congela todo a su paso.",                      "icono": "🧊❄"},
}

# Indica si las habilidades de cruza ya fueron registradas en el catálogo
habilidades_registradas = False


def registrar_habilidades_cruza():
    """
    Agrega las habilidades de cruza al CATALOGO_HABILIDADES de habilidad.py.
    Solo se ejecuta la primera vez (para no repetir trabajo).
    """
    global habilidades_registradas
    if habilidades_registradas:
        return

    from habilidad import Habilidad, CATALOGO_HABILIDADES

    for nombre, datos in HABILIDADES_CRUZA.items():
        if nombre not in CATALOGO_HABILIDADES:
            CATALOGO_HABILIDADES[nombre] = Habilidad(
                nombre=nombre,
                tipo=datos["tipo"],
                costo_mp=datos["costo_mp"],
                potencia=datos["potencia"],
                descripcion=datos["desc"],
                icono=datos["icono"],
            )

    habilidades_registradas = True


def resolver_tipo_hijo(tipo_resultado):
    """
    Mapea el tipo de cruza al tipo válido más cercano para que
    Criatura() pueda instanciarse sin errores.
    El tipo híbrido real se guarda en criatura._tipo_cruza.
    """
    mapa_tipos = {
        "Vapor":          "Agua",
        "Magma":          "Fuego",
        "Choque Térmico": "Fuego",
        "Plasma":         "Rayo",
        "Pantano":        "Tierra",
        "Escarcha":       "Agua",
        "Tormenta":       "Rayo",
        "Cristal":        "Tierra",
        "Metal":          "Tierra",
        "Aurora":         "Rayo",
    }
    return mapa_tipos.get(tipo_resultado, "Normal")


class ResultadoCruza:
    """
    Contiene el resultado de un cruzamiento entre dos criaturas.

    Atributos:
        criatura (Criatura):    La criatura hijo resultante.
        es_mutacion (bool):     True si ocurrió una mutación rara.
        nombre_mutacion (str):  Nombre de la mutación (vacío si no hubo).
        mensaje (str):          Descripción completa del resultado.
    """

    def __init__(self, criatura, es_mutacion, nombre_mutacion, mensaje):
        self.criatura        = criatura
        self.es_mutacion     = es_mutacion
        self.nombre_mutacion = nombre_mutacion
        self.mensaje         = mensaje


def cruzar(padre_a, padre_b):
    """
    Cruza dos criaturas y retorna un ResultadoCruza con el hijo generado.
    El hijo hereda estadísticas promediadas y escaladas según la tabla.
    Tiene 5% de probabilidad de ser una mutación rara.

    Lanza ValueError si la combinación de tipos no tiene cruza definida.
    """
    from criatura import Criatura
    from habilidad import CATALOGO_HABILIDADES

    tipo_a = padre_a.tipo.nombre
    tipo_b = padre_b.tipo.nombre

    # frozenset permite que Fuego x Agua == Agua x Fuego
    clave = frozenset({tipo_a, tipo_b})
    if clave not in TABLA_CRUZAS:
        combos = [" x ".join(sorted(k)) for k in TABLA_CRUZAS.keys()]
        raise ValueError(
            f"No existe cruza definida para {tipo_a} x {tipo_b}.\n"
            f"Combinaciones disponibles: {', '.join(combos)}"
        )

    datos = TABLA_CRUZAS[clave]

    # Calcular estadísticas base como promedio de los padres, escalado
    hp_base  = int(((padre_a.hp_max  + padre_b.hp_max)  / 2) * datos["escala_hp"])
    atk_base = int(((padre_a.atk     + padre_b.atk)     / 2) * datos["escala_atk"])
    def_base = int(((padre_a.defensa + padre_b.defensa) / 2) * datos["escala_def"])
    vel_base = int(((padre_a.velocidad + padre_b.velocidad) / 2) * datos["escala_vel"])

    # Garantizar mínimos
    hp_base  = max(50, hp_base)
    atk_base = max(20, atk_base)
    def_base = max(8,  def_base)
    vel_base = max(5,  vel_base)

    # El nivel del hijo es el promedio de los padres
    nivel_hijo = max(1, (padre_a.nivel + padre_b.nivel) // 2)

    # Determinar si hay mutación
    es_mutacion    = False
    datos_mutacion = {}
    tipo_resultado = datos["tipo_resultado"]

    if tipo_resultado in TABLA_MUTACIONES and random.random() < PROBABILIDAD_MUTACION:
        es_mutacion    = True
        datos_mutacion = TABLA_MUTACIONES[tipo_resultado]
        atk_base += datos_mutacion.get("bonus_atk", 0)
        def_base += datos_mutacion.get("bonus_def", 0)
        vel_base += datos_mutacion.get("bonus_vel", 0)
        hp_base  += datos_mutacion.get("bonus_hp",  0)

    if es_mutacion:
        nombre_hijo = datos_mutacion.get("nombre_mutacion", datos["nombre_base"])
    else:
        nombre_hijo = datos["nombre_base"]

    # Crear el hijo con el tipo base más cercano al híbrido
    tipo_hijo_str = resolver_tipo_hijo(tipo_resultado)
    hijo = Criatura(
        nombre=nombre_hijo,
        tipo=tipo_hijo_str,
        hp=hp_base,
        atk=atk_base,
        defensa=def_base,
        velocidad=vel_base,
        nivel=nivel_hijo,
        mp_max=int((padre_a.mp_max + padre_b.mp_max) / 2),
    )

    # Guardar metadata del tipo híbrido real para la GUI
    hijo.tipo_cruza    = tipo_resultado
    hijo.afinidad      = datos["afinidad"]
    hijo.desc_afinidad = datos["desc_afinidad"]
    hijo.es_cruza      = True
    hijo.es_mutacion   = es_mutacion
    if es_mutacion:
        hijo.icono_cruza = datos_mutacion.get("icono", datos["icono"])
        hijo.color_cruza = datos_mutacion.get("color", datos["color"])
    else:
        hijo.icono_cruza = datos["icono"]
        hijo.color_cruza = datos["color"]

    # Asignar habilidades exclusivas de la cruza
    registrar_habilidades_cruza()

    for nombre_hab in datos["habilidades_exclusivas"]:
        hab = CATALOGO_HABILIDADES.get(nombre_hab)
        if hab:
            hijo.agregar_habilidad(hab)

    if es_mutacion:
        nombre_extra = datos_mutacion.get("habilidad_extra", "")
        if nombre_extra and nombre_extra in CATALOGO_HABILIDADES:
            hijo.agregar_habilidad(CATALOGO_HABILIDADES[nombre_extra])

    # Construir mensaje de resultado
    lineas = []
    if es_mutacion:
        lineas.append(
            f"🌟 ¡MUTACIÓN RARA! "
            f"{padre_a.nombre} x {padre_b.nombre} -> {nombre_hijo}"
        )
        lineas.append(f"   {datos_mutacion.get('bonus_desc', '')}")
    else:
        lineas.append(
            f"✨ ¡Cruza exitosa! "
            f"{padre_a.nombre} ({tipo_a}) x {padre_b.nombre} ({tipo_b}) -> {nombre_hijo} ({tipo_resultado})"
        )
    lineas.append(
        f"   HP:{hp_base} ATK:{atk_base} DEF:{def_base} VEL:{vel_base} | Nv.{nivel_hijo}"
    )
    lineas.append(f"   Afinidad: {datos['desc_afinidad']}")
    habs = ", ".join(datos["habilidades_exclusivas"])
    if es_mutacion and datos_mutacion.get("habilidad_extra"):
        habs += f", {datos_mutacion['habilidad_extra']}"
    lineas.append(f"   Habilidades exclusivas: {habs}")

    return ResultadoCruza(
        criatura=hijo,
        es_mutacion=es_mutacion,
        nombre_mutacion=nombre_hijo if es_mutacion else "",
        mensaje="\n".join(lineas),
    )


def combinaciones_disponibles():
    """
    Retorna la lista de todas las combinaciones posibles con su metadata.
    Útil para mostrar en la GUI.
    """
    resultado = []
    for clave, datos in TABLA_CRUZAS.items():
        tipos          = sorted(clave)
        mutacion_info  = TABLA_MUTACIONES.get(datos["tipo_resultado"])
        resultado.append({
            "tipo_a":          tipos[0],
            "tipo_b":          tipos[1],
            "tipo_resultado":  datos["tipo_resultado"],
            "nombre_base":     datos["nombre_base"],
            "icono":           datos["icono"],
            "color":           datos["color"],
            "afinidad":        datos["afinidad"],
            "desc_afinidad":   datos["desc_afinidad"],
            "tiene_mutacion":  mutacion_info is not None,
            "nombre_mutacion": mutacion_info["nombre_mutacion"] if mutacion_info else None,
        })
    return resultado
