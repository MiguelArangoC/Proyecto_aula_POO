"""
cruza.py
========
Sistema de cruzamiento entre criaturas del juego Chronicle of Shadows.

Tabla de cruzas (tipo A × tipo B → tipo resultado):
  Fuego  × Agua   → Vapor
  Fuego  × Tierra → Magma
  Fuego  × Hielo  → Choque Térmico
  Fuego  × Rayo   → Plasma
  Agua   × Tierra → Pantano
  Agua   × Hielo  → Escarcha
  Agua   × Rayo   → Tormenta
  Tierra × Hielo  → Cristal
  Tierra × Rayo   → Metal
  Hielo  × Rayo   → Aurora

Cada tipo resultante tiene:
  - Stats base derivados del promedio ponderado de los padres.
  - Una afinidad especial (pasiva de combate).
  - Habilidades exclusivas desbloqueadas al nacer.

Mutaciones raras (5% de probabilidad):
  Plasma      → Plasma Alfa
  Cristal     → Cristal Corrupto
  (más en TABLA_MUTACIONES)
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from criatura import Criatura


# ─────────────────────────────────────────
# TABLA DE CRUZAS
# Clave: frozenset de dos tipos → dict con datos del hijo
# ─────────────────────────────────────────

TABLA_CRUZAS: dict[frozenset, dict] = {
    frozenset({"Fuego", "Agua"}): {
        "tipo_resultado":  "Vapor",
        "nombre_base":     "Vapora",
        "icono":           "💨",
        "color":           "#B0C4DE",
        "afinidad":        "evasion_fisica",
        "desc_afinidad":   "Envuelta en vapor, evade un 30% de los ataques físicos recibidos.",
        "escala_hp":       1.00,
        "escala_atk":      1.05,
        "escala_def":      1.00,
        "escala_vel":      1.15,
        "habilidades_exclusivas": ["Cortina de Vapor", "Burbuja Escaldante"],
    },
    frozenset({"Fuego", "Tierra"}): {
        "tipo_resultado":  "Magma",
        "nombre_base":     "Magmor",
        "icono":           "🌋",
        "color":           "#CC4400",
        "afinidad":        "resistencia_fuego",
        "desc_afinidad":   "Cuerpo de roca fundida: absorbe el 50% del daño de tipo Fuego.",
        "escala_hp":       1.10,
        "escala_atk":      1.10,
        "escala_def":      1.15,
        "escala_vel":      0.90,
        "habilidades_exclusivas": ["Oleada de Lava", "Coraza Ígnea"],
    },
    frozenset({"Fuego", "Hielo"}): {
        "tipo_resultado":  "Choque Térmico",
        "nombre_base":     "Termox",
        "icono":           "❄🔥",
        "color":           "#8A2BE2",
        "afinidad":        "confusion_termica",
        "desc_afinidad":   "Sus ataques tienen 25% de probabilidad de confundir al objetivo, reduciendo su precisión un turno.",
        "escala_hp":       1.05,
        "escala_atk":      1.20,
        "escala_def":      0.95,
        "escala_vel":      1.05,
        "habilidades_exclusivas": ["Pulso Dual", "Fractura Térmica"],
    },
    frozenset({"Fuego", "Rayo"}): {
        "tipo_resultado":  "Plasma",
        "nombre_base":     "Plasmar",
        "icono":           "⚡🔥",
        "color":           "#FFD700",
        "afinidad":        "sobrecarga",
        "desc_afinidad":   "Cada 3 turnos libera una descarga automática que hace 15 de daño fijo al enemigo.",
        "escala_hp":       0.95,
        "escala_atk":      1.25,
        "escala_def":      0.90,
        "escala_vel":      1.20,
        "habilidades_exclusivas": ["Arco de Plasma", "Nova Solar"],
    },
    frozenset({"Agua", "Tierra"}): {
        "tipo_resultado":  "Pantano",
        "nombre_base":     "Cenagar",
        "icono":           "🟫💧",
        "color":           "#556B2F",
        "afinidad":        "ralentizar",
        "desc_afinidad":   "Sus ataques reducen la velocidad del enemigo en 3 puntos durante 2 turnos.",
        "escala_hp":       1.12,
        "escala_atk":      1.00,
        "escala_def":      1.10,
        "escala_vel":      0.95,
        "habilidades_exclusivas": ["Trampa de Lodo", "Absorción Pantanosa"],
    },
    frozenset({"Agua", "Hielo"}): {
        "tipo_resultado":  "Escarcha",
        "nombre_base":     "Frostyn",
        "icono":           "🧊",
        "color":           "#ADD8E6",
        "afinidad":        "congelacion",
        "desc_afinidad":   "15% de probabilidad de congelar al objetivo por 1 turno (pierde su acción).",
        "escala_hp":       1.05,
        "escala_atk":      1.05,
        "escala_def":      1.10,
        "escala_vel":      1.00,
        "habilidades_exclusivas": ["Aliento Glacial", "Tormenta de Agujas"],
    },
    frozenset({"Agua", "Rayo"}): {
        "tipo_resultado":  "Tormenta",
        "nombre_base":     "Tempest",
        "icono":           "⛈",
        "color":           "#4682B4",
        "afinidad":        "cadena_electrica",
        "desc_afinidad":   "Al atacar, hay 20% de que el daño se encadene al turno siguiente como daño extra.",
        "escala_hp":       1.00,
        "escala_atk":      1.15,
        "escala_def":      1.00,
        "escala_vel":      1.10,
        "habilidades_exclusivas": ["Rayo Torrencial", "Ojo del Huracán"],
    },
    frozenset({"Tierra", "Hielo"}): {
        "tipo_resultado":  "Cristal",
        "nombre_base":     "Crystar",
        "icono":           "💎",
        "color":           "#E0FFFF",
        "afinidad":        "reflejo_daño",
        "desc_afinidad":   "Refleja el 20% del daño físico recibido de vuelta al atacante.",
        "escala_hp":       1.08,
        "escala_atk":      1.00,
        "escala_def":      1.20,
        "escala_vel":      0.95,
        "habilidades_exclusivas": ["Fragmento Cortante", "Armadura Cristalina"],
    },
    frozenset({"Tierra", "Rayo"}): {
        "tipo_resultado":  "Metal",
        "nombre_base":     "Ferron",
        "icono":           "⚙️",
        "color":           "#A9A9A9",
        "afinidad":        "blindaje_electrico",
        "desc_afinidad":   "Inmune al efecto de reducción de velocidad. Su DEF bloquea un 10% extra de daño.",
        "escala_hp":       1.10,
        "escala_atk":      1.05,
        "escala_def":      1.25,
        "escala_vel":      0.90,
        "habilidades_exclusivas": ["Carga Metálica", "Escudo Conductor"],
    },
    frozenset({"Hielo", "Rayo"}): {
        "tipo_resultado":  "Aurora",
        "nombre_base":     "Aurorix",
        "icono":           "🌌",
        "color":           "#DA70D6",
        "afinidad":        "aura_prismatica",
        "desc_afinidad":   "Al inicio de cada combate otorga +10% de ataque a todas las criaturas del equipo durante 3 turnos.",
        "escala_hp":       1.02,
        "escala_atk":      1.12,
        "escala_def":      1.05,
        "escala_vel":      1.12,
        "habilidades_exclusivas": ["Destello Boreal", "Prisma Cósmico"],
    },
}

# ─────────────────────────────────────────
# MUTACIONES RARAS
# tipo_resultado → datos de mutación
# ─────────────────────────────────────────

PROBABILIDAD_MUTACION: float = 0.05   # 5%

TABLA_MUTACIONES: dict[str, dict] = {
    "Plasma": {
        "nombre_mutacion":  "Plasma Alfa",
        "icono":            "⚡⚡",
        "color":            "#FF4500",
        "bonus_atk":        15,
        "bonus_vel":        10,
        "bonus_desc":       "ATK +15, VEL +10, habilidad exclusiva Overload.",
        "habilidad_extra":  "Overload",
    },
    "Cristal": {
        "nombre_mutacion":  "Cristal Corrupto",
        "icono":            "🖤💎",
        "color":            "#9400D3",
        "bonus_atk":        12,
        "bonus_def":        8,
        "bonus_desc":       "ATK +12, DEF +8, reflejo de daño sube al 35%.",
        "habilidad_extra":  "Espejo Oscuro",
    },
    "Aurora": {
        "nombre_mutacion":  "Aurora Caótica",
        "icono":            "🌌💥",
        "color":            "#FF1493",
        "bonus_atk":        10,
        "bonus_vel":        8,
        "bonus_hp":         20,
        "bonus_desc":       "HP +20, ATK +10, VEL +8. Aura prisma activa desde el turno 1.",
        "habilidad_extra":  "Caos Estelar",
    },
    "Tormenta": {
        "nombre_mutacion":  "Tormenta Perfecta",
        "icono":            "⛈⚡",
        "color":            "#00BFFF",
        "bonus_atk":        18,
        "bonus_desc":       "ATK +18. La cadena eléctrica activa al 40%.",
        "habilidad_extra":  "Tifón Eléctrico",
    },
    "Magma": {
        "nombre_mutacion":  "Magma Primordial",
        "icono":            "🌋🔴",
        "color":            "#FF6600",
        "bonus_hp":         25,
        "bonus_def":        10,
        "bonus_desc":       "HP +25, DEF +10. Absorbe el 75% del daño de Fuego.",
        "habilidad_extra":  "Núcleo Eterno",
    },
}

# ─────────────────────────────────────────
# HABILIDADES EXCLUSIVAS DE CRUZAS
# (se agregan al catálogo principal en runtime)
# ─────────────────────────────────────────

HABILIDADES_CRUZA: dict[str, dict] = {
    # ── Vapor ────────────────────────────────────────────────────────────
    "Cortina de Vapor": {
        "tipo": "esquivar", "costo_mp": 12, "potencia": 0.0,
        "desc": "Se envuelve en vapor denso. -60% de ser golpeado este turno.",
        "icono": "💨",
    },
    "Burbuja Escaldante": {
        "tipo": "especial", "costo_mp": 18, "potencia": 1.6,
        "desc": "Lanza burbujas de agua hirviendo que ignoran parte de la DEF.",
        "icono": "💨",
    },
    # ── Magma ────────────────────────────────────────────────────────────
    "Oleada de Lava": {
        "tipo": "especial", "costo_mp": 22, "potencia": 2.0,
        "desc": "Inunda el campo con roca fundida. Alto daño, penetra DEF.",
        "icono": "🌋",
    },
    "Coraza Ígnea": {
        "tipo": "soporte", "costo_mp": 16, "potencia": 0.20,
        "desc": "Endurece la piel con magma solidificado. Recupera 20% HP.",
        "icono": "🌋",
    },
    # ── Choque Térmico ───────────────────────────────────────────────────
    "Pulso Dual": {
        "tipo": "especial", "costo_mp": 20, "potencia": 1.7,
        "desc": "Dispara frío y calor simultáneos, perturbando al objetivo.",
        "icono": "❄🔥",
    },
    "Fractura Térmica": {
        "tipo": "especial", "costo_mp": 32, "potencia": 2.4,
        "desc": "Choque de temperaturas extremas que fractura la DEF enemiga.",
        "icono": "❄🔥",
    },
    # ── Plasma ───────────────────────────────────────────────────────────
    "Arco de Plasma": {
        "tipo": "especial", "costo_mp": 24, "potencia": 2.1,
        "desc": "Dispara un arco de plasma sobrecargado. Penetra toda la DEF.",
        "icono": "⚡🔥",
    },
    "Nova Solar": {
        "tipo": "especial", "costo_mp": 40, "potencia": 3.0,
        "desc": "Explosión de plasma solar. El ataque más poderoso de las cruzas.",
        "icono": "☀️⚡",
    },
    "Overload": {
        "tipo": "especial", "costo_mp": 35, "potencia": 2.8,
        "desc": "[MUTACIÓN] Sobrecarga total del sistema. Ignora DEF por completo.",
        "icono": "⚡⚡",
    },
    # ── Pantano ──────────────────────────────────────────────────────────
    "Trampa de Lodo": {
        "tipo": "ataque", "costo_mp": 14, "potencia": 1.3,
        "desc": "Atrapa al enemigo en lodo pegajoso, reduciendo su velocidad.",
        "icono": "🟫",
    },
    "Absorción Pantanosa": {
        "tipo": "soporte", "costo_mp": 20, "potencia": 0.30,
        "desc": "Absorbe la energía del entorno. Recupera 30% HP.",
        "icono": "🟫",
    },
    # ── Escarcha ─────────────────────────────────────────────────────────
    "Aliento Glacial": {
        "tipo": "especial", "costo_mp": 18, "potencia": 1.7,
        "desc": "Congela el aire al exhalar. Puede congelar al objetivo.",
        "icono": "🧊",
    },
    "Tormenta de Agujas": {
        "tipo": "especial", "costo_mp": 28, "potencia": 2.2,
        "desc": "Lluvia de cristales de hielo que perforan la DEF.",
        "icono": "🧊",
    },
    # ── Tormenta ─────────────────────────────────────────────────────────
    "Rayo Torrencial": {
        "tipo": "especial", "costo_mp": 22, "potencia": 1.9,
        "desc": "Rayo guiado por un chorro de agua. Alta precisión y daño.",
        "icono": "⛈",
    },
    "Ojo del Huracán": {
        "tipo": "esquivar", "costo_mp": 18, "potencia": 0.0,
        "desc": "Entra en el ojo del huracán. -65% de recibir ataques este turno.",
        "icono": "⛈",
    },
    "Tifón Eléctrico": {
        "tipo": "especial", "costo_mp": 38, "potencia": 2.7,
        "desc": "[MUTACIÓN] Vórtice eléctrico devastador con daño encadenado.",
        "icono": "⛈⚡",
    },
    # ── Cristal ──────────────────────────────────────────────────────────
    "Fragmento Cortante": {
        "tipo": "ataque", "costo_mp": 12, "potencia": 1.4,
        "desc": "Lanza fragmentos de cristal afilados. Alta probabilidad de golpear.",
        "icono": "💎",
    },
    "Armadura Cristalina": {
        "tipo": "soporte", "costo_mp": 22, "potencia": 0.15,
        "desc": "Cubre el cuerpo con cristal. Recupera 15% HP y activa reflejo.",
        "icono": "💎",
    },
    "Espejo Oscuro": {
        "tipo": "especial", "costo_mp": 30, "potencia": 0.0,
        "desc": "[MUTACIÓN] Devuelve el 35% del daño recibido este turno como daño al atacante.",
        "icono": "🖤💎",
    },
    # ── Metal ────────────────────────────────────────────────────────────
    "Carga Metálica": {
        "tipo": "ataque", "costo_mp": 16, "potencia": 1.5,
        "desc": "Embiste con cuerpo metálico. Ignora el 15% de DEF del rival.",
        "icono": "⚙️",
    },
    "Escudo Conductor": {
        "tipo": "soporte", "costo_mp": 20, "potencia": 0.20,
        "desc": "Genera un campo electromagnético. Recupera 20% HP y eleva DEF.",
        "icono": "⚙️",
    },
    "Núcleo Eterno": {
        "tipo": "soporte", "costo_mp": 28, "potencia": 0.40,
        "desc": "[MUTACIÓN] El núcleo de magma regenera 40% HP y restaura 20 MP extra.",
        "icono": "🌋🔴",
    },
    # ── Aurora ───────────────────────────────────────────────────────────
    "Destello Boreal": {
        "tipo": "especial", "costo_mp": 20, "potencia": 1.8,
        "desc": "Dispara prismas de luz polar que desorientan y dañan al enemigo.",
        "icono": "🌌",
    },
    "Prisma Cósmico": {
        "tipo": "especial", "costo_mp": 36, "potencia": 2.5,
        "desc": "Canaliza la luz de las auroras en un rayo destructor.",
        "icono": "🌌",
    },
    "Caos Estelar": {
        "tipo": "especial", "costo_mp": 40, "potencia": 2.9,
        "desc": "[MUTACIÓN] Explosión de energía estelar caótica. Daño masivo e impredecible.",
        "icono": "🌌💥",
    },
}


# ─────────────────────────────────────────
# RESULTADO DE CRUZA
# ─────────────────────────────────────────

class ResultadoCruza:
    """
    Encapsula el resultado de una cruza entre dos criaturas.

    Atributos:
        criatura (Criatura): La nueva criatura creada.
        es_mutacion (bool): Si True, la criatura es una mutación rara.
        nombre_mutacion (str): Nombre de la mutación (vacío si no aplica).
        mensaje (str): Texto descriptivo del resultado para la GUI.
    """
    def __init__(
        self,
        criatura: "Criatura",
        es_mutacion: bool,
        nombre_mutacion: str,
        mensaje: str,
    ) -> None:
        self.criatura = criatura
        self.es_mutacion = es_mutacion
        self.nombre_mutacion = nombre_mutacion
        self.mensaje = mensaje


# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL DE CRUZA
# ─────────────────────────────────────────

def cruzar(padre_a: "Criatura", padre_b: "Criatura") -> ResultadoCruza:
    """
    Cruza dos criaturas y retorna el resultado.

    El hijo hereda stats promediados y escalados según la tabla.
    Tiene 5% de probabilidad de ser una mutación rara.

    Parámetros:
        padre_a (Criatura): Primera criatura padre.
        padre_b (Criatura): Segunda criatura padre.

    Retorna:
        ResultadoCruza con la criatura hijo y metadata.

    Lanza:
        ValueError: Si la combinación de tipos no tiene cruza definida.
    """
    from criatura import Criatura
    from habilidad import Habilidad, CATALOGO_HABILIDADES

    tipo_a = padre_a.tipo.nombre
    tipo_b = padre_b.tipo.nombre

    clave = frozenset({tipo_a, tipo_b})
    if clave not in TABLA_CRUZAS:
        combos_disponibles = [
            " × ".join(sorted(k)) for k in TABLA_CRUZAS.keys()
        ]
        raise ValueError(
            f"No existe cruza definida para {tipo_a} × {tipo_b}.\n"
            f"Combinaciones disponibles:\n"
            + "\n".join(f"  • {c}" for c in combos_disponibles)
        )

    datos = TABLA_CRUZAS[clave]

    # — Stats base: promedio de padres escalado —
    hp_base  = int(((padre_a.hp_max  + padre_b.hp_max)  / 2) * datos["escala_hp"])
    atk_base = int(((padre_a.atk     + padre_b.atk)     / 2) * datos["escala_atk"])
    def_base = int(((padre_a.defensa + padre_b.defensa) / 2) * datos["escala_def"])
    vel_base = int(((padre_a.velocidad+ padre_b.velocidad)/2) * datos["escala_vel"])

    # Mínimos garantizados
    hp_base  = max(50, hp_base)
    atk_base = max(20, atk_base)
    def_base = max(8, def_base)
    vel_base = max(5, vel_base)

    # Nivel hijo = promedio de padres
    nivel_hijo = max(1, (padre_a.nivel + padre_b.nivel) // 2)

    # — Determinar mutación —
    es_mutacion = False
    datos_mutacion: dict = {}
    tipo_resultado = datos["tipo_resultado"]

    if tipo_resultado in TABLA_MUTACIONES and random.random() < PROBABILIDAD_MUTACION:
        es_mutacion = True
        datos_mutacion = TABLA_MUTACIONES[tipo_resultado]
        atk_base += datos_mutacion.get("bonus_atk", 0)
        def_base += datos_mutacion.get("bonus_def", 0)
        vel_base += datos_mutacion.get("bonus_vel", 0)
        hp_base  += datos_mutacion.get("bonus_hp", 0)

    nombre_hijo = (
        datos_mutacion.get("nombre_mutacion", datos["nombre_base"])
        if es_mutacion
        else datos["nombre_base"]
    )

    # — Crear la criatura hijo con su tipo híbrido real —
    # _resolver_tipo_gui() retorna el tipo de cruza directamente, ya que
    # todos los tipos híbridos (Vapor, Magma, etc.) están registrados en tipo.py.
    tipo_hijo_str = _resolver_tipo_gui(tipo_resultado)

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

    # Metadata extra para la GUI (no en sistema de tipos formal)
    hijo._tipo_cruza    = tipo_resultado
    hijo._afinidad      = datos["afinidad"]
    hijo._desc_afinidad = datos["desc_afinidad"]
    hijo._icono_cruza   = (
        datos_mutacion.get("icono", datos["icono"])
        if es_mutacion else datos["icono"]
    )
    hijo._color_cruza   = (
        datos_mutacion.get("color", datos["color"])
        if es_mutacion else datos["color"]
    )
    hijo._es_cruza = True
    hijo._es_mutacion = es_mutacion

    # — Habilidades: básica + exclusivas de la cruza —
    _registrar_habilidades_cruza()   # asegura que estén en el catálogo

    for nombre_hab in datos["habilidades_exclusivas"]:
        hab = CATALOGO_HABILIDADES.get(nombre_hab)
        if hab:
            hijo.agregar_habilidad(hab)

    if es_mutacion:
        nombre_extra = datos_mutacion.get("habilidad_extra", "")
        if nombre_extra and nombre_extra in CATALOGO_HABILIDADES:
            hijo.agregar_habilidad(CATALOGO_HABILIDADES[nombre_extra])

    # — Construir mensaje —
    lineas = []
    if es_mutacion:
        lineas.append(
            f"🌟 ¡MUTACIÓN RARA! "
            f"{padre_a.nombre} × {padre_b.nombre} → {nombre_hijo}"
        )
        lineas.append(f"   {datos_mutacion.get('bonus_desc', '')}")
    else:
        lineas.append(
            f"✨ ¡Cruza exitosa! "
            f"{padre_a.nombre} ({tipo_a}) × {padre_b.nombre} ({tipo_b}) → {nombre_hijo} ({tipo_resultado})"
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


# ─────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────

def _resolver_tipo_gui(tipo_resultado: str) -> str:
    """
    Retorna el tipo elemental real de la criatura de cruza.

    Todos los tipos híbridos (Vapor, Magma, Choque Térmico, Plasma, Pantano,
    Escarcha, Tormenta, Cristal, Metal, Aurora) están registrados en tipo.py
    como tipos completamente válidos con su propia tabla de multiplicadores,
    por lo que se retorna el nombre de cruza directamente.

    Parámetros:
        tipo_resultado (str): El tipo de cruza tal como aparece en TABLA_CRUZAS.

    Retorna:
        str: El mismo tipo_resultado si es válido; 'Normal' como último recurso.
    """
    from tipo import TIPOS_VALIDOS
    if tipo_resultado in TIPOS_VALIDOS:
        return tipo_resultado
    # Fallback de seguridad (no debería ocurrir con las cruzas definidas)
    return "Normal"


_habilidades_registradas = False

def _registrar_habilidades_cruza() -> None:
    """
    Agrega las habilidades de cruza al CATALOGO_HABILIDADES de habilidad.py
    la primera vez que se invoca (lazy registration).
    """
    global _habilidades_registradas
    if _habilidades_registradas:
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

    _habilidades_registradas = True


def combinaciones_disponibles() -> list[dict]:
    """
    Retorna lista de todas las combinaciones posibles con metadata,
    útil para mostrar en la GUI.
    """
    resultado = []
    for clave, datos in TABLA_CRUZAS.items():
        tipos = sorted(clave)
        mutacion_info = TABLA_MUTACIONES.get(datos["tipo_resultado"])
        resultado.append({
            "tipo_a":         tipos[0],
            "tipo_b":         tipos[1],
            "tipo_resultado": datos["tipo_resultado"],
            "nombre_base":    datos["nombre_base"],
            "icono":          datos["icono"],
            "color":          datos["color"],
            "afinidad":       datos["afinidad"],
            "desc_afinidad":  datos["desc_afinidad"],
            "tiene_mutacion": mutacion_info is not None,
            "nombre_mutacion": mutacion_info["nombre_mutacion"] if mutacion_info else None,
        })
    return resultado