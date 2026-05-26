"""
criatura.py
===========
Define la clase Criatura, que representa las entidades que el jugador
puede capturar y usar en combate.

Atributos de combate: HP, MP, ATK, DEF, VEL, precisión, nivel, XP.
Sistema de habilidades: lista de objetos Habilidad.
Sistema de evolución: hasta 2 etapas usando Fragmentos de Evolución.
"""

from tipo import Tipo
from habilidad import CATALOGO_HABILIDADES


# ─────────────────────────────────────────
# ÁRBOL DE EVOLUCIONES
# ─────────────────────────────────────────
# Estructura: nombre_base -> { etapa: { datos de evolución } }
# Las escalas se aplican sobre los stats actuales de la criatura.

ARBOL_EVOLUCIONES = {
    "Ignis": {
        1: {
            "nombre":             "Ignis Ardiente",
            "fragmento":          "Fragmento de Llama",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Llamarada"],
                CATALOGO_HABILIDADES["Paso Sombra"],
            ],
            "escala_hp":   1.20,
            "escala_atk":  1.25,
            "escala_def":  1.10,
            "escala_vel":  1.15,
            "mp_max_nuevo": 60,
        },
        2: {
            "nombre":             "Ignis Magna",
            "fragmento":          "Fragmento de Llama",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Colmillo Ígneo"],
                CATALOGO_HABILIDADES["Erupción Solar"],
                CATALOGO_HABILIDADES["Brisa Curativa"],
            ],
            "escala_hp":   1.30,
            "escala_atk":  1.35,
            "escala_def":  1.15,
            "escala_vel":  1.20,
            "mp_max_nuevo": 100,
        },
    },
    "Ignis Ardiente": {
        2: {
            "nombre":             "Ignis Magna",
            "fragmento":          "Fragmento de Llama",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Colmillo Ígneo"],
                CATALOGO_HABILIDADES["Erupción Solar"],
                CATALOGO_HABILIDADES["Brisa Curativa"],
            ],
            "escala_hp":   1.30,
            "escala_atk":  1.35,
            "escala_def":  1.15,
            "escala_vel":  1.20,
            "mp_max_nuevo": 100,
        },
    },
    "Torrente": {
        1: {
            "nombre":             "Torrente Furioso",
            "fragmento":          "Fragmento de Marea",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Squirt de Agua"],
                CATALOGO_HABILIDADES["Aura de Tormenta"],
            ],
            "escala_hp":   1.22,
            "escala_atk":  1.20,
            "escala_def":  1.18,
            "escala_vel":  1.12,
            "mp_max_nuevo": 65,
        },
        2: {
            "nombre":             "Torrente Magna",
            "fragmento":          "Fragmento de Marea",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Vórtice"],
                CATALOGO_HABILIDADES["Marea Abismal"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.28,
            "escala_atk":  1.30,
            "escala_def":  1.20,
            "escala_vel":  1.18,
            "mp_max_nuevo": 110,
        },
    },
    "Torrente Furioso": {
        2: {
            "nombre":             "Torrente Magna",
            "fragmento":          "Fragmento de Marea",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Vórtice"],
                CATALOGO_HABILIDADES["Marea Abismal"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.28,
            "escala_atk":  1.30,
            "escala_def":  1.20,
            "escala_vel":  1.18,
            "mp_max_nuevo": 110,
        },
    },
    "Rocafer": {
        1: {
            "nombre":             "Rocafer Colosal",
            "fragmento":          "Fragmento de Tierra",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Pedrada"],
                CATALOGO_HABILIDADES["Paso Sombra"],
            ],
            "escala_hp":   1.28,
            "escala_atk":  1.18,
            "escala_def":  1.30,
            "escala_vel":  1.05,
            "mp_max_nuevo": 55,
        },
        2: {
            "nombre":             "Rocafer Magna",
            "fragmento":          "Fragmento de Tierra",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Terremoto Menor"],
                CATALOGO_HABILIDADES["Colapso Tectónico"],
                CATALOGO_HABILIDADES["Brisa Curativa"],
            ],
            "escala_hp":   1.35,
            "escala_atk":  1.22,
            "escala_def":  1.40,
            "escala_vel":  1.08,
            "mp_max_nuevo": 90,
        },
    },
    "Rocafer Colosal": {
        2: {
            "nombre":             "Rocafer Magna",
            "fragmento":          "Fragmento de Tierra",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Terremoto Menor"],
                CATALOGO_HABILIDADES["Colapso Tectónico"],
                CATALOGO_HABILIDADES["Brisa Curativa"],
            ],
            "escala_hp":   1.35,
            "escala_atk":  1.22,
            "escala_def":  1.40,
            "escala_vel":  1.08,
            "mp_max_nuevo": 90,
        },
    },
    "Voltex": {
        1: {
            "nombre":             "Voltex Ionico",
            "fragmento":          "Fragmento de Trueno",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Chispa"],
                CATALOGO_HABILIDADES["Aura de Tormenta"],
            ],
            "escala_hp":   1.18,
            "escala_atk":  1.28,
            "escala_def":  1.10,
            "escala_vel":  1.25,
            "mp_max_nuevo": 70,
        },
        2: {
            "nombre":             "Voltex Magna",
            "fragmento":          "Fragmento de Trueno",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Rayo Cruzado"],
                CATALOGO_HABILIDADES["Tormenta Ionica"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.25,
            "escala_atk":  1.35,
            "escala_def":  1.14,
            "escala_vel":  1.25,
            "mp_max_nuevo": 115,
        },
    },
    "Voltex Ionico": {
        2: {
            "nombre":             "Voltex Magna",
            "fragmento":          "Fragmento de Trueno",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Rayo Cruzado"],
                CATALOGO_HABILIDADES["Tormenta Ionica"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.25,
            "escala_atk":  1.35,
            "escala_def":  1.14,
            "escala_vel":  1.25,
            "mp_max_nuevo": 115,
        },
    },
    "Glacius": {
        1: {
            "nombre":             "Glacius Boreal",
            "fragmento":          "Fragmento de Escarcha",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Lanza de Hielo"],
                CATALOGO_HABILIDADES["Paso Sombra"],
            ],
            "escala_hp":   1.20,
            "escala_atk":  1.22,
            "escala_def":  1.15,
            "escala_vel":  1.12,
            "mp_max_nuevo": 62,
        },
        2: {
            "nombre":             "Glacius Magna",
            "fragmento":          "Fragmento de Escarcha",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Ventisca"],
                CATALOGO_HABILIDADES["Cero Absoluto"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.30,
            "escala_atk":  1.32,
            "escala_def":  1.20,
            "escala_vel":  1.18,
            "mp_max_nuevo": 105,
        },
    },
    "Glacius Boreal": {
        2: {
            "nombre":             "Glacius Magna",
            "fragmento":          "Fragmento de Escarcha",
            "habilidades_nuevas": [
                CATALOGO_HABILIDADES["Ventisca"],
                CATALOGO_HABILIDADES["Cero Absoluto"],
                CATALOGO_HABILIDADES["Pulso Vital"],
            ],
            "escala_hp":   1.30,
            "escala_atk":  1.32,
            "escala_def":  1.20,
            "escala_vel":  1.18,
            "mp_max_nuevo": 105,
        },
    },
}


class Criatura:
    """
    Representa una criatura del juego con atributos de combate y progresión.

    Atributos:
        nombre (str):       Nombre actual (cambia al evolucionar).
        nombre_base (str):  Nombre original (no cambia nunca).
        tipo (Tipo):        Tipo elemental.
        hp / hp_max (int):  Puntos de vida actuales y máximos.
        mp / mp_max (int):  Puntos de magia actuales y máximos.
        atk (int):          Poder de ataque.
        defensa (int):      Reducción de daño recibido.
        velocidad (int):    Determina quién ataca primero.
        precision (float):  Probabilidad de acertar (0.0 a 1.0).
        nivel (int):        Nivel actual de la criatura.
        experiencia (int):  XP acumulada hacia el siguiente nivel.
        habilidades (list): Lista de objetos Habilidad disponibles.
        forma (int):        Etapa evolutiva (0 = base, 1 = primera, 2 = Magna).
        _evasivo (bool):    Marca temporal de esquiva para el turno actual.
    """

    XP_BASE               = 100
    XP_FACTOR             = 1.5
    MP_RECUPERACION_TURNO = 8   # MP que recupera automáticamente cada turno

    def __init__(
        self,
        nombre,
        tipo,
        hp,
        atk,
        defensa=10,
        velocidad=10,
        precision=0.90,
        nivel=1,
        mp_max=40,
        forma=0,
    ):
        if hp <= 0 or atk <= 0 or defensa <= 0:
            raise ValueError("hp, atk y defensa deben ser mayores que 0.")
        if not (0.0 <= precision <= 1.0):
            raise ValueError("precision debe estar entre 0.0 y 1.0.")

        self.nombre      = nombre
        self.nombre_base = nombre        # se mantiene aunque evolucione
        self.tipo        = Tipo(tipo)
        self.hp          = hp
        self.hp_max      = hp
        self.mp          = mp_max
        self.mp_max      = mp_max
        self.atk         = atk
        self.defensa     = defensa
        self.velocidad   = velocidad
        self.precision   = precision
        self.nivel       = nivel
        self.experiencia = 0
        self.xp_siguiente = int(self.XP_BASE * (self.XP_FACTOR ** (nivel - 1)))
        self.item_equipado = None
        self.forma       = forma
        self.evasivo    = False

        # Siempre incluye Atacar como habilidad base
        self.habilidades = [CATALOGO_HABILIDADES["Atacar"]]

    # ─────────────────────────────────────────
    # ESTADO
    # ─────────────────────────────────────────

    def esta_debilitada(self):
        """Retorna True si la criatura no tiene HP disponible."""
        return self.hp <= 0

    def recuperar_mp_turno(self):
        """Recupera MP pasivo al inicio de cada turno."""
        self.mp = min(self.mp_max, self.mp + self.MP_RECUPERACION_TURNO)

    def limpiar_estado_turno(self):
        """Limpia el estado evasivo al final del turno."""
        self.evasivo = False

    # ─────────────────────────────────────────
    # HABILIDADES
    # ─────────────────────────────────────────

    def agregar_habilidad(self, habilidad):
        """Agrega una habilidad si aún no está en la lista."""
        nombres_actuales = [h.nombre for h in self.habilidades]
        if habilidad.nombre not in nombres_actuales:
            self.habilidades.append(habilidad)

    def obtener_habilidad(self, nombre):
        """Retorna la habilidad con el nombre dado, o None si no existe."""
        for h in self.habilidades:
            if h.nombre == nombre:
                return h
        return None

    # ─────────────────────────────────────────
    # EVOLUCIÓN
    # ─────────────────────────────────────────

    def puede_evolucionar(self, fragmento):
        """
        Verifica si la criatura puede evolucionar con el fragmento dado.
        Retorna (True, "") si puede, o (False, motivo) si no puede.
        """
        if self.forma >= 2:
            return False, f"{self.nombre} ya alcanzó su forma máxima (Magna)."

        siguiente_forma = self.forma + 1
        datos = ARBOL_EVOLUCIONES.get(self.nombre, {}).get(siguiente_forma)
        if datos is None:
            return False, f"{self.nombre} no tiene evolución definida."

        if fragmento.nombre != datos["fragmento"]:
            return False, (
                f"{self.nombre} necesita un {datos['fragmento']} "
                f"para evolucionar, no un {fragmento.nombre}."
            )

        return True, ""

    def evolucionar(self, fragmento):
        """
        Evoluciona la criatura consumiendo el fragmento indicado.
        Escala las estadísticas, actualiza el nombre y desbloquea habilidades.
        Retorna un mensaje descriptivo del proceso.
        """
        puede, motivo = self.puede_evolucionar(fragmento)
        if not puede:
            raise ValueError(motivo)

        siguiente_forma = self.forma + 1
        datos           = ARBOL_EVOLUCIONES[self.nombre][siguiente_forma]

        nombre_anterior = self.nombre
        nombre_nuevo    = datos["nombre"]

        # Escalar estadísticas
        self.hp_max    = int(self.hp_max   * datos["escala_hp"])
        self.hp        = self.hp_max        # restaura HP completo al evolucionar
        self.atk       = int(self.atk      * datos["escala_atk"])
        self.defensa   = int(self.defensa  * datos["escala_def"])
        self.velocidad = int(self.velocidad* datos["escala_vel"])
        self.mp_max    = datos["mp_max_nuevo"]
        self.mp        = self.mp_max        # restaura MP completo

        # Actualizar nombre y etapa evolutiva
        self.nombre = nombre_nuevo
        self.forma  = siguiente_forma

        # Desbloquear habilidades nuevas
        for h in datos["habilidades_nuevas"]:
            self.agregar_habilidad(h)

        nombres_nuevas = ", ".join(h.nombre for h in datos["habilidades_nuevas"])
        if siguiente_forma == 1:
            etapa = "Primera Evolución"
        else:
            etapa = "Forma Magna"

        return (
            f"✨ ¡{nombre_anterior} evolucionó a {nombre_nuevo}! [{etapa}]\n"
            f"   HP: {self.hp_max} | ATK: {self.atk} | DEF: {self.defensa} "
            f"| VEL: {self.velocidad} | MP: {self.mp_max}\n"
            f"   Nuevas habilidades: {nombres_nuevas}"
        )

    # ─────────────────────────────────────────
    # PROGRESIÓN
    # ─────────────────────────────────────────

    def ganar_experiencia(self, xp):
        """
        Agrega experiencia y sube de nivel si corresponde.
        Retorna True si la criatura subió de nivel.
        """
        if xp <= 0:
            raise ValueError("La experiencia ganada debe ser mayor que 0.")
        self.experiencia += xp
        subio = False
        while self.experiencia >= self.xp_siguiente:
            self.subir_nivel()
            subio = True
        return subio

    def subir_nivel(self):
        """Sube un nivel y escala todas las estadísticas."""
        self.experiencia  -= self.xp_siguiente
        self.nivel        += 1
        self.xp_siguiente  = int(self.XP_BASE * (self.XP_FACTOR ** (self.nivel - 1)))
        self.hp_max        = int(self.hp_max   * 1.10)
        self.hp            = self.hp_max
        self.mp_max        = int(self.mp_max   * 1.08)
        self.mp            = self.mp_max
        self.atk           = int(self.atk      * 1.08)
        self.defensa       = int(self.defensa  * 1.05)
        self.velocidad     = int(self.velocidad* 1.05)

    # ─────────────────────────────────────────
    # REPRESENTACIÓN
    # ─────────────────────────────────────────

    def __repr__(self):
        return (
            f"Criatura(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"hp={self.hp}/{self.hp_max}, mp={self.mp}/{self.mp_max}, "
            f"nivel={self.nivel}, forma={self.forma})"
        )

    def __str__(self):
        if self.item_equipado:
            item_str = f" [{self.item_equipado.nombre}]"
        else:
            item_str = ""
        habs = ", ".join(h.nombre for h in self.habilidades)
        return (
            f"{self.nombre} (Nv.{self.nivel} | {self.tipo} | Forma {self.forma}){item_str}\n"
            f"  HP:{self.hp}/{self.hp_max}  MP:{self.mp}/{self.mp_max}  "
            f"ATK:{self.atk}  DEF:{self.defensa}  VEL:{self.velocidad}\n"
            f"  Habilidades: {habs}"
        )
