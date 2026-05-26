"""
game_state.py
=============
Backend del juego de Criaturas por Turnos.
La clase Juego orquesta todos los módulos: Jugador, Mapa, Batalla,
ítems y persistencia. La interfaz gráfica (GUI) solo llama métodos
de esta clase; nunca accede directamente al modelo.
"""

import os
import random
import sys

from criatura import Criatura
from jugador import Jugador, cargar_jugador
from mapa import crear_mapa_default
from batalla import Batalla, EstadoBatalla
from item import Item
from fragmento import FragmentoEvolucion, CATALOGO_FRAGMENTOS, PROBABILIDAD_DROP_FRAGMENTO
from excepciones import (
    EquipoLlenoError,
    CapturaFallidaError,
    ItemNoDisponibleError,
    CriaturaDebilitadaError,
    PartidaNoEncontradaError,
    ZonaInexistenteError,
)


def ruta_partida_default():
    """Retorna la ruta de partida.json junto al ejecutable o al proyecto."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "partida.json")


# ─────────────────────────────────────────
# CATÁLOGO DE CRIATURAS Y ÍTEMS
# ─────────────────────────────────────────

CATALOGO_CRIATURAS = {
    "Ignis":    {"tipo": "Fuego",  "hp": 100, "atk": 50, "defensa": 12, "velocidad": 14},
    "Torrente": {"tipo": "Agua",   "hp": 110, "atk": 45, "defensa": 14, "velocidad": 12},
    "Rocafer":  {"tipo": "Tierra", "hp": 130, "atk": 40, "defensa": 18, "velocidad": 8},
    "Voltex":   {"tipo": "Rayo",   "hp": 90,  "atk": 60, "defensa": 10, "velocidad": 18},
    "Glacius":  {"tipo": "Hielo",  "hp": 105, "atk": 52, "defensa": 13, "velocidad": 13},
}

CATALOGO_ITEMS = {
    "Poción": {
        "descripcion":     "Restaura 30 HP a la criatura equipada.",
        "efecto_positivo": {"hp": 30},
        "efecto_negativo": {},
        "es_consumible":   True,
        "es_captura":      False,
    },
    "Amuleto de Fuego": {
        "descripcion":     "Aumenta el ATK +10 pero reduce la DEF -5.",
        "efecto_positivo": {"atk": 10},
        "efecto_negativo": {"defensa": 5},
        "es_consumible":   False,
        "es_captura":      False,
    },
    "Escudo Terrenal": {
        "descripcion":     "Aumenta la DEF +15 pero reduce la VEL -3.",
        "efecto_positivo": {"defensa": 15},
        "efecto_negativo": {"velocidad": 3},
        "es_consumible":   False,
        "es_captura":      False,
    },
    "Trampa Básica": {
        "descripcion":     "Permite intentar capturar una criatura salvaje.",
        "efecto_positivo": {},
        "efecto_negativo": {},
        "es_consumible":   True,
        "es_captura":      True,
    },
}

# Qué fragmento puede aparecer en cada zona (None = ninguno)
ZONA_FRAGMENTO = {
    "Volcán":        "Fragmento de Llama",
    "Lago":          "Fragmento de Marea",
    "Cueva de Roca": "Fragmento de Tierra",
    "Cumbre Nevada": ["Fragmento de Escarcha", "Fragmento de Trueno"],
    "Pradera":       None,
}


def crear_criatura(nombre):
    """Instancia una Criatura desde el catálogo."""
    datos = CATALOGO_CRIATURAS[nombre]
    return Criatura(
        nombre=nombre,
        tipo=datos["tipo"],
        hp=datos["hp"],
        atk=datos["atk"],
        defensa=datos["defensa"],
        velocidad=datos["velocidad"],
    )


def _crear_item(nombre):
    """Instancia un Item desde el catálogo."""
    datos = CATALOGO_ITEMS[nombre]
    return Item(
        nombre=nombre,
        descripcion=datos["descripcion"],
        efecto_positivo=datos["efecto_positivo"],
        efecto_negativo=datos["efecto_negativo"],
        es_consumible=datos["es_consumible"],
        es_captura=datos["es_captura"],
    )


# ─────────────────────────────────────────
# CLASE PRINCIPAL DEL JUEGO
# ─────────────────────────────────────────

class Juego:
    """
    Orquesta toda la lógica del juego y expone métodos simples para la GUI.
    """

    def __init__(self):
        self.jugador            = None
        self.mapa               = crear_mapa_default()
        self.batalla_activa     = None
        self.criatura_encontrada = None

    def validar_jugador(self):
        """Verifica que haya un jugador creado antes de ejecutar cualquier acción."""
        if self.jugador is None:
            raise ValueError("No hay jugador creado. Llama a crear_jugador() primero.")

    # ─────────────────────────────────────────
    # RF1 — CREAR JUGADOR
    # ─────────────────────────────────────────

    def crear_jugador(self, nombre, criatura_inicial="Ignis", oro_inicial=200):
        if criatura_inicial not in {"Ignis", "Torrente", "Rocafer"}:
            raise ValueError("La criatura inicial debe ser Ignis, Torrente o Rocafer.")
        self.jugador = Jugador(nombre, oro=oro_inicial)
        self.jugador.agregar_criatura(crear_criatura(criatura_inicial))
        self.jugador.agregar_item(_crear_item("Poción"))
        self.jugador.agregar_item(_crear_item("Trampa Básica"))
        return (
            f"¡Bienvenido, {nombre}! Empiezas en la Pradera con {criatura_inicial} "
            f"y {self.jugador.oro} de oro."
        )

    # ─────────────────────────────────────────
    # RF2 — EXPLORAR / MOVER
    # ─────────────────────────────────────────

    def obtener_zona_actual(self):
        self.validar_jugador()
        return self.jugador.posicion

    def obtener_conexiones(self):
        self.validar_jugador()
        return self.mapa.zonas_adyacentes(self.jugador.posicion)

    def mover(self, direccion):
        self.validar_jugador()
        if self.batalla_activa and self.batalla_activa.estado == EstadoBatalla.EN_CURSO:
            raise ValueError("No puedes moverte de zona mientras estés en combate.")
        conexiones = self.obtener_conexiones()
        if direccion not in conexiones:
            raise ValueError(
                f"No puedes ir al '{direccion}' desde {self.jugador.posicion}. "
                f"Direcciones disponibles: {list(conexiones.keys())}"
            )
        destino           = conexiones[direccion]
        self.jugador.posicion = destino
        zona              = self.mapa.obtener_zona(destino)
        return f"Te moviste a {destino} [{zona.clima_base}]."

    def mini_mapa(self):
        self.validar_jugador()
        zonas = ["Volcán", "Cueva de Roca", "Cumbre Nevada", "Pradera", "Lago"]
        marcas = {}
        for z in zonas:
            if z == self.jugador.posicion:
                marcas[z] = "[X]"
            else:
                marcas[z] = "[ ]"
        return (
            "Mini mapa:\n"
            f"  {marcas['Volcán']} Volcán -- {marcas['Cueva de Roca']} Cueva de Roca\n"
            f"                         |\n"
            f"                 {marcas['Cumbre Nevada']} Cumbre Nevada\n"
            f"      |\n"
            f"  {marcas['Pradera']} Pradera -- {marcas['Lago']} Lago"
        )

    def explorar(self):
        """
        Intenta generar un encuentro con una criatura salvaje (60% prob).
        En zonas con fragmento asignado, también puede dropar uno (25% prob).
        """
        self.validar_jugador()
        if self.batalla_activa and self.batalla_activa.estado == EstadoBatalla.EN_CURSO:
            raise ValueError("Ya hay una batalla en curso.")

        mensajes     = []
        zona_nombre  = self.jugador.posicion

        # Posible drop de fragmento
        nombre_fragmento = ZONA_FRAGMENTO.get(zona_nombre)
        if nombre_fragmento and random.random() < PROBABILIDAD_DROP_FRAGMENTO:
            if isinstance(nombre_fragmento, list):
                nombre_fragmento = random.choice(nombre_fragmento)
            frag = FragmentoEvolucion(nombre_fragmento)
            self.jugador.inventario.append(frag)
            mensajes.append(f"✨ ¡Encontraste un {nombre_fragmento}! Se guardó en tu inventario.")

        # Posible encuentro de criatura (60% de probabilidad)
        if random.random() >= 0.60:
            if mensajes:
                mensajes.append("Exploraste la zona pero no encontraste ninguna criatura.")
                return "\n".join(mensajes)
            return "Exploraste la zona pero no encontraste nada."

        zona             = self.mapa.obtener_zona(zona_nombre)
        nombre_criatura  = zona.obtener_criatura_aleatoria()
        if not nombre_criatura:
            mensajes.append("Esta zona no tiene criaturas salvajes.")
            return "\n".join(mensajes)

        self.criatura_encontrada = crear_criatura(nombre_criatura)
        mensajes.append(f"¡Apareció un {nombre_criatura} salvaje!")
        return "\n".join(mensajes)

    # ─────────────────────────────────────────
    # RF4 / RF5 — INICIAR BATALLA Y TURNO
    # ─────────────────────────────────────────

    def iniciar_batalla(self):
        self.validar_jugador()
        if self.criatura_encontrada is None:
            raise ValueError("No hay criatura salvaje para batallar. Explora primero.")

        zona = self.mapa.obtener_zona(self.jugador.posicion)
        self.batalla_activa = Batalla(
            self.jugador,
            self.criatura_encontrada,
            nombre_clima=zona.clima_base,
        )
        return self.batalla_activa.log[0]

    def ejecutar_turno(self, usar_item=False, nombre_item="", nombre_habilidad=""):
        """
        Ejecuta un turno de la batalla activa.
        Retorna un dict con: estado, log, resumen y habilidad_usada.
        """
        if self.batalla_activa is None:
            raise ValueError("No hay batalla activa.")

        log_antes    = len(self.batalla_activa.log)
        estado       = self.batalla_activa.ejecutar_turno(
            usar_item=usar_item,
            nombre_item=nombre_item,
            nombre_habilidad=nombre_habilidad,
        )
        nuevos_eventos = self.batalla_activa.log[log_antes:]

        if estado != EstadoBatalla.EN_CURSO:
            self.criatura_encontrada = None

        return {
            "estado":         estado.name,
            "log":            nuevos_eventos,
            "resumen":        self.batalla_activa.resumen(),
            "habilidad_usada": nombre_habilidad or "Atacar",
        }

    def retirarse(self):
        if self.batalla_activa is None:
            raise ValueError("No hay batalla activa.")
        self.batalla_activa.retirarse()
        self.criatura_encontrada = None
        return f"{self.jugador.nombre} se retiró de la batalla."

    def hay_batalla_activa(self):
        return (
            self.batalla_activa is not None
            and self.batalla_activa.estado == EstadoBatalla.EN_CURSO
        )

    def hay_criatura_encontrada(self):
        return self.criatura_encontrada is not None

    # ─────────────────────────────────────────
    # RF3 — CAPTURAR CRIATURA
    # ─────────────────────────────────────────

    def capturar(self, nombre_item_captura):
        self.validar_jugador()
        if self.criatura_encontrada is None:
            raise ValueError("No hay criatura salvaje para capturar.")
        try:
            self.jugador.capturar_criatura(self.criatura_encontrada, nombre_item_captura)
            nombre = self.criatura_encontrada.nombre
            self.criatura_encontrada = None
            return f"¡{nombre} fue capturado y se unió a tu equipo!"
        except CapturaFallidaError:
            if not self.hay_batalla_activa():
                self.criatura_encontrada = None
            raise

    def intentar_captura_en_batalla(self, nombre_item_captura):
        self.validar_jugador()
        if self.batalla_activa is None:
            raise ValueError("No hay batalla activa.")
        if self.criatura_encontrada is None:
            raise ValueError("No hay criatura salvaje para capturar.")

        try:
            self.jugador.capturar_criatura(self.criatura_encontrada, nombre_item_captura)
            nombre = self.criatura_encontrada.nombre
            self.criatura_encontrada = None
            self.batalla_activa.estado = EstadoBatalla.VICTORIA
            self.batalla_activa.registrar(f"¡{nombre} fue capturado y se unió a tu equipo!")
            msg = f"¡{nombre} fue capturado y se unió a tu equipo!"
            self.batalla_activa = None
            return msg
        except CapturaFallidaError:
            self.batalla_activa.registrar(
                f"Intento de captura de "
                f"{self.criatura_encontrada.nombre} con {nombre_item_captura} falló."
            )

            criatura_jugador = self.jugador.criatura_activa()
            if criatura_jugador is None:
                self.batalla_activa.estado = EstadoBatalla.DERROTA
                raise

            criatura_jugador.recuperar_mp_turno()

            dano_j = self.batalla_activa.condicion_climatica.aplicar_dano_turno(criatura_jugador)
            dano_e = self.batalla_activa.condicion_climatica.aplicar_dano_turno(self.batalla_activa.enemigo)
            if dano_j:
                self.batalla_activa.registrar(
                    f"El clima {self.batalla_activa.condicion_climatica.nombre} hace "
                    f"{dano_j} de daño a {criatura_jugador.nombre}."
                )
            if dano_e:
                self.batalla_activa.registrar(
                    f"El clima {self.batalla_activa.condicion_climatica.nombre} hace "
                    f"{dano_e} de daño a {self.batalla_activa.enemigo.nombre}."
                )

            if not self.batalla_activa.verificar_fin():
                self.batalla_activa.turno_enemigo(criatura_jugador)
                self.batalla_activa.verificar_fin()

            criatura_jugador.limpiar_estado_turno()
            self.batalla_activa.turno += 1
            raise

    # ─────────────────────────────────────────
    # RF6 — EQUIPAR ÍTEM
    # ─────────────────────────────────────────

    def equipar_item(self, indice_criatura, nombre_item):
        self.validar_jugador()
        if indice_criatura < 0 or indice_criatura >= len(self.jugador.equipo):
            raise IndexError(f"No existe una criatura en la posición {indice_criatura}.")
        criatura = self.jugador.equipo[indice_criatura]
        self.jugador.equipar_item(criatura, nombre_item)
        return f"{nombre_item} equipado a {criatura.nombre}."

    def agregar_item_inventario(self, nombre_item):
        self.validar_jugador()
        if nombre_item not in CATALOGO_ITEMS:
            raise KeyError(f"'{nombre_item}' no existe en el catálogo de ítems.")
        self.jugador.agregar_item(_crear_item(nombre_item))
        return f"{nombre_item} agregado al inventario."

    # ─────────────────────────────────────────
    # EVOLUCIONAR CRIATURA
    # ─────────────────────────────────────────

    def evolucionar_criatura(self, nombre_criatura):
        """
        Evoluciona la criatura indicada consumiendo el fragmento correcto del inventario.
        Retorna un mensaje descriptivo del resultado.
        """
        self.validar_jugador()
        criatura = None
        for c in self.jugador.equipo:
            if c.nombre == nombre_criatura:
                criatura = c
                break
        if criatura is None:
            raise ValueError(f"Criatura '{nombre_criatura}' no encontrada en el equipo.")

        # Buscar un fragmento compatible en el inventario
        fragmento = None
        for item in self.jugador.inventario:
            if getattr(item, "es_fragmento", False):
                puede, _ = criatura.puede_evolucionar(item)
                if puede:
                    fragmento = item
                    break

        if fragmento is None:
            siguiente = criatura.forma + 1
            from criatura import ARBOL_EVOLUCIONES
            datos_evo = ARBOL_EVOLUCIONES.get(criatura.nombre, {}).get(siguiente)
            if datos_evo:
                raise ValueError(
                    f"{criatura.nombre} necesita un {datos_evo['fragmento']} "
                    f"para evolucionar. ¡Encuéntralo explorando la zona correcta!"
                )
            raise ValueError(f"{criatura.nombre} no tiene evolución definida o ya alcanzó su forma máxima.")

        msg = criatura.evolucionar(fragmento)
        self.jugador.inventario.remove(fragmento)
        return msg

    def set_criatura_combate(self, nombre_criatura):
        """Marca la criatura que el jugador eligió para el combate."""
        self.validar_jugador()
        self.jugador.set_criatura_combate(nombre_criatura)

    def liberar_criatura(self, nombre_criatura):
        """Elimina una criatura del equipo de forma voluntaria."""
        self.validar_jugador()
        self.jugador.remover_criatura(nombre_criatura)
        return f"{nombre_criatura} ha sido liberado del equipo."

    def habilidades_criatura_activa(self):
        """Retorna las habilidades de la criatura activa del jugador como lista de dicts."""
        self.validar_jugador()
        criatura = self.jugador.criatura_activa()
        if criatura is None:
            return []
        resultado = []
        for h in criatura.habilidades:
            resultado.append({
                "nombre":      h.nombre,
                "tipo":        h.tipo,
                "costo_mp":    h.costo_mp,
                "potencia":    h.potencia,
                "descripcion": h.descripcion,
                "icono":       h.icono,
                "puede_usar":  criatura.mp >= h.costo_mp,
            })
        return resultado

    # ─────────────────────────────────────────
    # RF7 — CONSULTAR EQUIPO E INVENTARIO
    # ─────────────────────────────────────────

    def estado_equipo(self):
        self.validar_jugador()
        resultado = []
        for c in self.jugador.equipo:
            resultado.append({
                "nombre":        c.nombre,
                "tipo":          c.tipo.nombre,
                "nivel":         c.nivel,
                "hp":            c.hp,
                "hp_max":        c.hp_max,
                "mp":            c.mp,
                "mp_max":        c.mp_max,
                "atk":           c.atk,
                "defensa":       c.defensa,
                "velocidad":     c.velocidad,
                "experiencia":   c.experiencia,
                "xp_siguiente":  c.xp_siguiente,
                "item_equipado": c.item_equipado.nombre if c.item_equipado else "Ninguno",
                "debilitada":    c.esta_debilitada(),
                "forma":         c.forma,
                "habilidades":   [h.nombre for h in c.habilidades],
            })
        return resultado

    def estado_inventario(self):
        """Retorna ítems e incluye FragmentoEvolucion como tipo especial."""
        self.validar_jugador()
        resultado = []
        for i in self.jugador.inventario:
            if getattr(i, "es_fragmento", False):
                resultado.append({
                    "nombre":          i.nombre,
                    "descripcion":     i.descripcion,
                    "es_consumible":   True,
                    "es_captura":      False,
                    "es_fragmento":    True,
                    "efecto_positivo": {},
                    "efecto_negativo": {},
                    "icono":           i.icono,
                    "tipo_criatura":   i.tipo_criatura,
                })
            else:
                resultado.append({
                    "nombre":          i.nombre,
                    "descripcion":     i.descripcion,
                    "es_consumible":   i.es_consumible,
                    "es_captura":      i.es_captura,
                    "es_fragmento":    False,
                    "efecto_positivo": i.efecto_positivo,
                    "efecto_negativo": i.efecto_negativo,
                })
        return resultado

    def items_captura_disponibles(self):
        self.validar_jugador()
        resultado = []
        for i in self.jugador.inventario:
            if i.es_captura:
                resultado.append(i.nombre)
        return resultado

    def info_zona_actual(self):
        self.validar_jugador()
        zona             = self.mapa.obtener_zona(self.jugador.posicion)
        tiene_fragmento  = ZONA_FRAGMENTO.get(zona.nombre) is not None
        return {
            "nombre":             zona.nombre,
            "clima_base":         zona.clima_base,
            "criaturas_salvajes": zona.criaturas_salvajes,
            "conexiones":         zona.conexiones,
            "mini_mapa":          self.mini_mapa(),
            "fragmento_zona":     ZONA_FRAGMENTO.get(zona.nombre),
            "tiene_fragmento":    tiene_fragmento,
        }

    # ─────────────────────────────────────────
    # RF10 — GUARDAR Y CARGAR PARTIDA
    # ─────────────────────────────────────────

    def guardar_partida(self, ruta=None):
        if ruta is None:
            ruta = ruta_partida_default()
        self.validar_jugador()
        self.jugador.guardar(ruta)
        return f"Partida guardada en '{ruta}'."

    def cargar_partida(self, ruta=None):
        if ruta is None:
            ruta = ruta_partida_default()
        self.jugador             = cargar_jugador(ruta)
        self.batalla_activa      = None
        self.criatura_encontrada = None
        return (
            f"Partida cargada. Bienvenido de nuevo, {self.jugador.nombre}. "
            f"Estás en {self.jugador.posicion}."
        )

    def hay_partida_guardada(self, ruta=None):
        if ruta is None:
            ruta = ruta_partida_default()
        return os.path.isfile(ruta)
