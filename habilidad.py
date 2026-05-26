"""
habilidad.py
============
Define la clase Habilidad, que representa una acción que una criatura
puede ejecutar en combate.

Tipos de habilidad
------------------
  "ataque"   — inflige daño directo al enemigo.
  "especial" — daño amplificado que ignora parte de la DEF del enemigo.
  "esquivar" — el usuario entra en modo evasivo: los ataques que recibe
               este turno tienen -50% de probabilidad de conectar.
  "soporte"  — restaura HP del usuario.
"""

import random


class Habilidad:
    """
    Representa una habilidad usable en combate.

    Atributos:
        nombre (str):        Nombre de la habilidad.
        tipo (str):          Categoría: 'ataque', 'especial', 'esquivar' o 'soporte'.
        costo_mp (int):      MP que consume al usarse (0 para el ataque básico).
        potencia (float):    Multiplicador de daño sobre el ATK base.
        precision_mod (float): Modificador sobre la precisión base del usuario.
        descripcion (str):   Texto descriptivo para la GUI.
        icono (str):         Emoji representativo para la GUI.
    """

    def __init__(
        self,
        nombre,
        tipo,
        costo_mp,
        potencia,
        precision_mod=1.0,
        descripcion="",
        icono="✦",
    ):
        tipos_validos = {"ataque", "especial", "esquivar", "soporte"}
        if tipo not in tipos_validos:
            raise ValueError(f"Tipo '{tipo}' no válido. Use: {tipos_validos}")
        if potencia < 0:
            raise ValueError("La potencia no puede ser negativa.")
        if costo_mp < 0:
            raise ValueError("El costo de MP no puede ser negativo.")

        self.nombre        = nombre
        self.tipo          = tipo
        self.costo_mp      = costo_mp
        self.potencia      = potencia
        self.precision_mod = precision_mod
        self.descripcion   = descripcion
        self.icono         = icono

    def puede_usarse(self, usuario):
        """Retorna True si el usuario tiene suficiente MP para esta habilidad."""
        return usuario.mp >= self.costo_mp

    def usar(self, usuario, objetivo, mod_clima=1.0):
        """
        Ejecuta la habilidad y retorna un diccionario con el resultado.

        Retorna un dict con:
            "conecto"  (bool) — si la acción tuvo efecto.
            "dano"     (int)  — daño infligido (0 si no aplica).
            "curacion" (int)  — HP restaurado (0 si no aplica).
            "evasion"  (bool) — si el usuario entró en estado evasivo.
            "mensaje"  (str)  — descripción del evento para el log.
        """
        resultado = {
            "conecto":  False,
            "dano":     0,
            "curacion": 0,
            "evasion":  False,
            "mensaje":  "",
        }

        # Verificar MP
        if not self.puede_usarse(usuario):
            resultado["mensaje"] = (
                f"{usuario.nombre} no tiene MP suficiente para {self.nombre}. "
                f"(Necesita {self.costo_mp} MP, tiene {usuario.mp} MP)"
            )
            return resultado

        # Consumir MP
        usuario.mp = max(0, usuario.mp - self.costo_mp)

        # ── ATAQUE NORMAL ─────────────────────────────────────────────────
        if self.tipo == "ataque":
            precision_efectiva = min(1.0, usuario.precision * self.precision_mod)
            if random.random() > precision_efectiva:
                resultado["mensaje"] = f"{usuario.nombre} usó {self.nombre} pero falló."
                return resultado

            dano_base = random.randint(
                int(usuario.atk * self.potencia * 0.85),
                int(usuario.atk * self.potencia * 1.15),
            )
            mult_tipo  = usuario.tipo.calcular_multiplicador(objetivo.tipo)
            dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - objetivo.defensa // 2)

            objetivo.hp = max(0, objetivo.hp - dano_final)
            resultado["conecto"] = True
            resultado["dano"]    = dano_final
            resultado["mensaje"] = (
                f"{usuario.nombre} usó {self.nombre} -> {dano_final} de daño "
                f"a {objetivo.nombre} (tipo x{mult_tipo:.2f})."
            )

        # ── ATAQUE ESPECIAL ────────────────────────────────────────────────
        elif self.tipo == "especial":
            precision_efectiva = min(1.0, usuario.precision * self.precision_mod)
            if random.random() > precision_efectiva:
                resultado["mensaje"] = f"{usuario.nombre} usó {self.nombre} pero falló."
                return resultado

            dano_base = random.randint(
                int(usuario.atk * self.potencia * 0.90),
                int(usuario.atk * self.potencia * 1.10),
            )
            mult_tipo  = usuario.tipo.calcular_multiplicador(objetivo.tipo)
            # Los ataques especiales penetran el 70% de la DEF del objetivo
            dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - int(objetivo.defensa * 0.30))

            objetivo.hp = max(0, objetivo.hp - dano_final)
            resultado["conecto"] = True
            resultado["dano"]    = dano_final
            resultado["mensaje"] = (
                f"{usuario.nombre} usó {self.nombre} [ESPECIAL] -> {dano_final} de daño "
                f"a {objetivo.nombre} (ignora parte de la DEF)."
            )

        # ── ESQUIVAR ───────────────────────────────────────────────────────
        elif self.tipo == "esquivar":
            usuario.evasivo      = True
            resultado["conecto"]  = True
            resultado["evasion"]  = True
            resultado["mensaje"]  = (
                f"💨 {usuario.nombre} usó {self.nombre}: "
                f"los ataques que reciba este turno tienen -50% de probabilidad de conectar."
            )

        # ── SOPORTE ────────────────────────────────────────────────────────
        elif self.tipo == "soporte":
            curacion = int(usuario.hp_max * self.potencia)
            usuario.hp = min(usuario.hp_max, usuario.hp + curacion)
            resultado["conecto"]  = True
            resultado["curacion"] = curacion
            resultado["mensaje"]  = (
                f"💚 {usuario.nombre} usó {self.nombre}: recuperó {curacion} HP. "
                f"({usuario.hp}/{usuario.hp_max})"
            )

        return resultado

    def __repr__(self):
        return (
            f"Habilidad(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"costo_mp={self.costo_mp}, potencia={self.potencia})"
        )

    def __str__(self):
        return (
            f"{self.icono} {self.nombre} [{self.tipo.upper()}] "
            f"MP:{self.costo_mp} | POT:{self.potencia:.1f}x — {self.descripcion}"
        )


# ─────────────────────────────────────────
# CATÁLOGO DE HABILIDADES
# ─────────────────────────────────────────
# Diccionario nombre -> objeto Habilidad.
# Se importa desde criatura.py y game_state.py para asignar habilidades.

CATALOGO_HABILIDADES = {
    # Básica (todas las criaturas en forma base)
    "Atacar": Habilidad(
        nombre="Atacar", tipo="ataque", costo_mp=0, potencia=1.0,
        descripcion="Ataque físico básico.", icono="⚔",
    ),

    # Ignis (Fuego)
    "Llamarada": Habilidad(
        nombre="Llamarada", tipo="ataque", costo_mp=10, potencia=1.4,
        precision_mod=0.95, descripcion="Ataque de fuego de mediana potencia.", icono="🔥",
    ),
    "Colmillo Ígneo": Habilidad(
        nombre="Colmillo Ígneo", tipo="especial", costo_mp=20, potencia=1.8,
        precision_mod=0.88, descripcion="Mordida envuelta en llamas. Ignora parte de la defensa.", icono="🔥",
    ),
    "Erupción Solar": Habilidad(
        nombre="Erupción Solar", tipo="especial", costo_mp=35, potencia=2.6,
        precision_mod=0.80, descripcion="Explosión de plasma incandescente. Solo en forma Magna.", icono="☀",
    ),

    # Torrente (Agua)
    "Squirt de Agua": Habilidad(
        nombre="Squirt de Agua", tipo="ataque", costo_mp=10, potencia=1.4,
        precision_mod=0.95, descripcion="Disparo de agua a presión.", icono="💧",
    ),
    "Vórtice": Habilidad(
        nombre="Vórtice", tipo="especial", costo_mp=22, potencia=1.9,
        precision_mod=0.85, descripcion="Torbellino de agua que arrastra al objetivo. Penetra defensa.", icono="🌊",
    ),
    "Marea Abismal": Habilidad(
        nombre="Marea Abismal", tipo="especial", costo_mp=38, potencia=2.7,
        precision_mod=0.78, descripcion="Oleada colosal desde las profundidades. Solo en forma Magna.", icono="🌊",
    ),

    # Rocafer (Tierra)
    "Pedrada": Habilidad(
        nombre="Pedrada", tipo="ataque", costo_mp=10, potencia=1.3,
        precision_mod=0.98, descripcion="Lanza una roca sólida. Alta precisión.", icono="🪨",
    ),
    "Terremoto Menor": Habilidad(
        nombre="Terremoto Menor", tipo="especial", costo_mp=20, potencia=1.7,
        precision_mod=0.90, descripcion="Sacudida sísmica localizada. Penetra la defensa.", icono="🪨",
    ),
    "Colapso Tectónico": Habilidad(
        nombre="Colapso Tectónico", tipo="especial", costo_mp=40, potencia=2.5,
        precision_mod=0.82, descripcion="El suelo se rompe bajo el objetivo. Solo en forma Magna.", icono="⛰",
    ),

    # Glacius (Hielo)
    "Lanza de Hielo": Habilidad(
        nombre="Lanza de Hielo", tipo="ataque", costo_mp=10, potencia=1.35,
        precision_mod=0.96, descripcion="Proyectil helado de buena precisión.", icono="❄️",
    ),
    "Ventisca": Habilidad(
        nombre="Ventisca", tipo="especial", costo_mp=22, potencia=1.85,
        precision_mod=0.86, descripcion="Ráfaga glacial que penetra parte de la defensa.", icono="❄️",
    ),
    "Cero Absoluto": Habilidad(
        nombre="Cero Absoluto", tipo="especial", costo_mp=40, potencia=2.65,
        precision_mod=0.78, descripcion="Congelación extrema. Solo en forma Magna.", icono="❄️",
    ),

    # Voltex (Rayo)
    "Chispa": Habilidad(
        nombre="Chispa", tipo="ataque", costo_mp=10, potencia=1.35,
        precision_mod=0.97, descripcion="Descarga eléctrica rápida.", icono="⚡",
    ),
    "Rayo Cruzado": Habilidad(
        nombre="Rayo Cruzado", tipo="especial", costo_mp=23, potencia=1.9,
        precision_mod=0.84, descripcion="Impacto eléctrico concentrado que ignora parte de la defensa.", icono="⚡",
    ),
    "Tormenta Ionica": Habilidad(
        nombre="Tormenta Ionica", tipo="especial", costo_mp=42, potencia=2.75,
        precision_mod=0.76, descripcion="Campo eléctrico devastador. Solo en forma Magna.", icono="⚡",
    ),

    # Esquiva y soporte (universales)
    "Paso Sombra": Habilidad(
        nombre="Paso Sombra", tipo="esquivar", costo_mp=15, potencia=0.0,
        descripcion="Se funde con las sombras. Los ataques este turno tienen -50% de acierto.", icono="💨",
    ),
    "Aura de Tormenta": Habilidad(
        nombre="Aura de Tormenta", tipo="esquivar", costo_mp=20, potencia=0.0,
        descripcion="Genera un campo eléctrico disuasorio. Desvía ataques este turno.", icono="⚡",
    ),
    "Brisa Curativa": Habilidad(
        nombre="Brisa Curativa", tipo="soporte", costo_mp=18, potencia=0.25,
        descripcion="Recupera el 25% del HP máximo.", icono="💚",
    ),
    "Pulso Vital": Habilidad(
        nombre="Pulso Vital", tipo="soporte", costo_mp=30, potencia=0.40,
        descripcion="Regeneración profunda. Recupera el 40% del HP máximo.", icono="💚",
    ),
}
