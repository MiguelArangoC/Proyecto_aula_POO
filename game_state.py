"""
game_state.py
=============
Backend del juego de Criaturas por Turnos.
Expone la clase Juego que orquesta todos los módulos: Jugador, Mapa,
Batalla, ítems y persistencia. La interfaz gráfica (GUI) solo llama
métodos de esta clase; nunca accede directamente al modelo.

Cambios en esta versión
-----------------------
  - explorar() puede dropar FragmentoEvolucion en zonas con fragmento asignado.
  - ejecutar_turno() acepta nombre_habilidad para usar habilidades reales.
  - Nuevo método evolucionar_criatura() que consume el fragmento del inventario.
  - items_captura_disponibles() también devuelve nombres de fragmentos.
  - estado_inventario() incluye fragmentos serializados.
"""

from __future__ import annotations
import os
import random
import sys
from typing import Optional


def ruta_partida_default() -> str:
    """Ruta de partida.json junto al .exe (PyInstaller) o al proyecto."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "partida.json")

from criatura import Criatura
from jugador import Jugador
from mapa import Mapa
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


# ─────────────────────────────────────────
# CATÁLOGO DE CRIATURAS Y ÍTEMS
# ─────────────────────────────────────────

CATALOGO_CRIATURAS: dict[str, dict] = {
    "Ignis":    {"tipo": "Fuego",  "hp": 100, "atk": 50, "defensa": 12, "velocidad": 14},
    "Torrente": {"tipo": "Agua",   "hp": 110, "atk": 45, "defensa": 14, "velocidad": 12},
    "Rocafer":  {"tipo": "Tierra", "hp": 130, "atk": 40, "defensa": 18, "velocidad": 8},
    "Voltex":   {"tipo": "Rayo",   "hp": 90,  "atk": 60, "defensa": 10, "velocidad": 18},
    "Glacius":  {"tipo": "Hielo",  "hp": 105, "atk": 52, "defensa": 13, "velocidad": 13},
}

CATALOGO_ITEMS: dict[str, dict] = {
    "Poción": {
        "descripcion": "Restaura 30 HP a la criatura equipada.",
        "efecto_positivo": {"hp": 30},
        "efecto_negativo": {},
        "es_consumible": True,
        "es_captura": False,
    },
    "Amuleto de Fuego": {
        "descripcion": "Aumenta el ATK +10 pero reduce la DEF -5.",
        "efecto_positivo": {"atk": 10},
        "efecto_negativo": {"defensa": 5},
        "es_consumible": False,
        "es_captura": False,
    },
    "Escudo Terrenal": {
        "descripcion": "Aumenta la DEF +15 pero reduce la VEL -3.",
        "efecto_positivo": {"defensa": 15},
        "efecto_negativo": {"velocidad": 3},
        "es_consumible": False,
        "es_captura": False,
    },
    "Trampa Básica": {
        "descripcion": "Permite intentar capturar una criatura salvaje.",
        "efecto_positivo": {},
        "efecto_negativo": {},
        "es_consumible": True,
        "es_captura": True,
    },
}

# Qué fragmento puede dropar cada zona (None = ninguno)
_ZONA_FRAGMENTO: dict[str, Optional[str | list[str]]] = {
    "Volcán":        "Fragmento de Llama",
    "Lago":          "Fragmento de Marea",
    "Cueva de Roca": "Fragmento de Tierra",
    "Cumbre Nevada": ["Fragmento de Escarcha", "Fragmento de Trueno"],
    "Pradera":       None,
}


def _crear_criatura(nombre: str) -> Criatura:
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


def _crear_item(nombre: str) -> Item:
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

    def __init__(self) -> None:
        self.jugador: Optional[Jugador] = None
        self.mapa: Mapa = Mapa.crear_mapa_default()
        self.batalla_activa: Optional[Batalla] = None
        self.criatura_encontrada: Optional[Criatura] = None

    # ─────────────────────────────────────────
    # RF1 — CREAR JUGADOR
    # ─────────────────────────────────────────

    def crear_jugador(self, nombre: str, criatura_inicial: str = "Ignis", oro_inicial: int = 200) -> str:
        if criatura_inicial not in {"Ignis", "Torrente", "Rocafer"}:
            raise ValueError("La criatura inicial debe ser Ignis, Torrente o Rocafer.")
        self.jugador = Jugador(nombre, oro=oro_inicial)
        self.jugador.agregar_criatura(_crear_criatura(criatura_inicial))
        self.jugador.agregar_item(_crear_item("Poción"))
        self.jugador.agregar_item(_crear_item("Trampa Básica"))
        return (
            f"¡Bienvenido, {nombre}! Empiezas en la Pradera con {criatura_inicial} "
            f"y {self.jugador.oro} de oro."
        )

    # ─────────────────────────────────────────
    # RF2 — EXPLORAR / MOVER
    # ─────────────────────────────────────────

    def obtener_zona_actual(self) -> str:
        self._validar_jugador()
        return self.jugador.posicion

    def obtener_conexiones(self) -> dict[str, str]:
        self._validar_jugador()
        return self.mapa.zonas_adyacentes(self.jugador.posicion)

    def mover(self, direccion: str) -> str:
        self._validar_jugador()
        if self.batalla_activa and self.batalla_activa.estado == EstadoBatalla.EN_CURSO:
            raise RuntimeError("No puedes moverte de zona mientras estés en combate.")
        conexiones = self.obtener_conexiones()
        if direccion not in conexiones:
            raise ValueError(
                f"No puedes ir al '{direccion}' desde {self.jugador.posicion}. "
                f"Direcciones disponibles: {list(conexiones.keys())}"
            )
        destino = conexiones[direccion]
        self.jugador.posicion = destino
        zona = self.mapa.obtener_zona(destino)
        return f"Te moviste a {destino} [{zona.clima_base}]."

    def mini_mapa(self) -> str:
        self._validar_jugador()
        zonas = ["Volcán", "Cueva de Roca", "Cumbre Nevada", "Pradera", "Lago"]
        marcas = {z: ("[X]" if z == self.jugador.posicion else "[ ]") for z in zonas}
        return (
            "Mini mapa:\n"
            f"  {marcas['Volcán']} Volcán -- {marcas['Cueva de Roca']} Cueva de Roca\n"
            f"                         |\n"
            f"                 {marcas['Cumbre Nevada']} Cumbre Nevada\n"
            f"      |\n"
            f"  {marcas['Pradera']} Pradera -- {marcas['Lago']} Lago"
        )

    # ─────────────────────────────────────────
    # RF4 / RF5 — INICIAR BATALLA Y TURNO
    # ─────────────────────────────────────────

    def explorar(self) -> str:
        """
        Intenta generar un encuentro con una criatura salvaje (60% prob).
        Adicionalmente, en zonas con fragmento asignado, puede dropar un
        FragmentoEvolucion (PROBABILIDAD_DROP_FRAGMENTO independiente).

        Retorna un mensaje que describe lo ocurrido.
        """
        self._validar_jugador()
        if self.batalla_activa and self.batalla_activa.estado == EstadoBatalla.EN_CURSO:
            raise RuntimeError("Ya hay una batalla en curso.")

        mensajes: list[str] = []

        # — Posible drop de fragmento —
        zona_nombre = self.jugador.posicion
        nombre_fragmento = _ZONA_FRAGMENTO.get(zona_nombre)
        if nombre_fragmento and random.random() < PROBABILIDAD_DROP_FRAGMENTO:
            if isinstance(nombre_fragmento, list):
                nombre_fragmento = random.choice(nombre_fragmento)
            frag = FragmentoEvolucion(nombre_fragmento)
            # Guardamos en inventario como objeto "especial" (duck-typing)
            self.jugador.inventario.append(frag)
            mensajes.append(f"✨ ¡Encontraste un {nombre_fragmento}! Se guardó en tu inventario.")

        # — Posible encuentro de criatura —
        if random.random() >= 0.60:
            mensajes.append("Exploraste la zona pero no encontraste ninguna criatura.")
            return "\n".join(mensajes) if mensajes else "Exploraste la zona pero no encontraste nada."

        zona = self.mapa.obtener_zona(zona_nombre)
        nombre_criatura = zona.obtener_criatura_aleatoria()
        if not nombre_criatura:
            mensajes.append("Esta zona no tiene criaturas salvajes.")
            return "\n".join(mensajes)

        self.criatura_encontrada = _crear_criatura(nombre_criatura)
        mensajes.append(f"¡Apareció un {nombre_criatura} salvaje!")
        return "\n".join(mensajes)

    def iniciar_batalla(self) -> str:
        self._validar_jugador()
        if self.criatura_encontrada is None:
            raise RuntimeError("No hay criatura salvaje para batallar. Explora primero.")

        zona = self.mapa.obtener_zona(self.jugador.posicion)
        self.batalla_activa = Batalla(
            self.jugador,
            self.criatura_encontrada,
            nombre_clima=zona.clima_base,
        )
        return self.batalla_activa.log[0]

    def ejecutar_turno(
        self,
        usar_item: bool = False,
        nombre_item: str = "",
        nombre_habilidad: str = "",
    ) -> dict:
        """
        Ejecuta un turno de la batalla activa.

        Parámetros adicionales respecto a la versión anterior:
            nombre_habilidad (str): Nombre de la habilidad que usará la criatura
                del jugador este turno. Si está vacío se usa 'Atacar'.

        Retorna:
            dict con estado, log, resumen y (nuevo) habilidad_usada.
        """
        if self.batalla_activa is None:
            raise RuntimeError("No hay batalla activa.")

        log_antes = len(self.batalla_activa.log)
        estado = self.batalla_activa.ejecutar_turno(
            usar_item=usar_item,
            nombre_item=nombre_item,
            nombre_habilidad=nombre_habilidad,
        )
        nuevos_eventos = self.batalla_activa.log[log_antes:]

        if estado != EstadoBatalla.EN_CURSO:
            self.criatura_encontrada = None

        return {
            "estado": estado.name,
            "log": nuevos_eventos,
            "resumen": self.batalla_activa.resumen(),
            "habilidad_usada": nombre_habilidad or "Atacar",
        }

    def retirarse(self) -> str:
        if self.batalla_activa is None:
            raise RuntimeError("No hay batalla activa.")
        self.batalla_activa.retirarse()
        self.criatura_encontrada = None
        return f"{self.jugador.nombre} se retiró de la batalla."

    def hay_batalla_activa(self) -> bool:
        return (
            self.batalla_activa is not None
            and self.batalla_activa.estado == EstadoBatalla.EN_CURSO
        )

    def hay_criatura_encontrada(self) -> bool:
        return self.criatura_encontrada is not None

    # ─────────────────────────────────────────
    # RF3 — CAPTURAR CRIATURA
    # ─────────────────────────────────────────

    def capturar(self, nombre_item_captura: str) -> str:
        self._validar_jugador()
        if self.criatura_encontrada is None:
            raise RuntimeError("No hay criatura salvaje para capturar.")
        try:
            self.jugador.capturar_criatura(self.criatura_encontrada, nombre_item_captura)
            nombre = self.criatura_encontrada.nombre
            self.criatura_encontrada = None
            return f"¡{nombre} fue capturado y se unió a tu equipo!"
        except CapturaFallidaError:
            if not self.hay_batalla_activa():
                self.criatura_encontrada = None
            raise

    def intentar_captura_en_batalla(self, nombre_item_captura: str) -> str:
        self._validar_jugador()
        if self.batalla_activa is None:
            raise RuntimeError("No hay batalla activa.")
        if self.criatura_encontrada is None:
            raise RuntimeError("No hay criatura salvaje para capturar.")

        try:
            self.jugador.capturar_criatura(self.criatura_encontrada, nombre_item_captura)
            nombre = self.criatura_encontrada.nombre
            self.criatura_encontrada = None
            self.batalla_activa.estado = EstadoBatalla.VICTORIA
            self.batalla_activa._registrar(f"¡{nombre} fue capturado y se unió a tu equipo!")
            msg = f"¡{nombre} fue capturado y se unió a tu equipo!"
            self.batalla_activa = None
            return msg
        except CapturaFallidaError as e:
            # Si falla, consume el turno del jugador y el enemigo ataca.
            self.batalla_activa._registrar(f"[Turno {self.batalla_activa.turno}] Intento de captura de {self.criatura_encontrada.nombre} con {nombre_item_captura} falló.")
            
            criatura_jugador = self.jugador.criatura_activa()
            if criatura_jugador is None:
                self.batalla_activa.estado = EstadoBatalla.DERROTA
                raise

            # 1. Recuperar MP del jugador
            criatura_jugador.recuperar_mp_turno()

            # 2. Daño climático
            dano_j = self.batalla_activa.condicion_climatica.aplicar_dano_turno(criatura_jugador)
            dano_e = self.batalla_activa.condicion_climatica.aplicar_dano_turno(self.batalla_activa.enemigo)
            if dano_j:
                self.batalla_activa._registrar(
                    f"El clima {self.batalla_activa.condicion_climatica.nombre} hace "
                    f"{dano_j} de daño a {criatura_jugador.nombre}."
                )
            if dano_e:
                self.batalla_activa._registrar(
                    f"El clima {self.batalla_activa.condicion_climatica.nombre} hace "
                    f"{dano_e} de daño a {self.batalla_activa.enemigo.nombre}."
                )

            # Verificar si alguien murió por clima
            if not self.batalla_activa._verificar_fin():
                # 3. El enemigo ataca
                self.batalla_activa._turno_enemigo(criatura_jugador)
                self.batalla_activa._verificar_fin()

            # Limpiar estado temporal de esquiva
            criatura_jugador.limpiar_estado_turno()
            self.batalla_activa.turno += 1
            raise

    # ─────────────────────────────────────────
    # RF6 — EQUIPAR ÍTEM
    # ─────────────────────────────────────────

    def equipar_item(self, indice_criatura: int, nombre_item: str) -> str:
        self._validar_jugador()
        if indice_criatura < 0 or indice_criatura >= len(self.jugador.equipo):
            raise IndexError(f"No existe una criatura en la posición {indice_criatura}.")
        criatura = self.jugador.equipo[indice_criatura]
        self.jugador.equipar_item(criatura, nombre_item)
        return f"{nombre_item} equipado a {criatura.nombre}."

    def agregar_item_inventario(self, nombre_item: str) -> str:
        self._validar_jugador()
        if nombre_item not in CATALOGO_ITEMS:
            raise KeyError(f"'{nombre_item}' no existe en el catálogo de ítems.")
        self.jugador.agregar_item(_crear_item(nombre_item))
        return f"{nombre_item} agregado al inventario."

    # ─────────────────────────────────────────
    # NUEVO — EVOLUCIONAR CRIATURA
    # ─────────────────────────────────────────

    def evolucionar_criatura(self, nombre_criatura: str) -> str:
        """
        Evoluciona la criatura indicada consumiendo el fragmento correcto
        del inventario del jugador.

        Retorna:
            str: Mensaje descriptivo del resultado.

        Lanza:
            ValueError: Si la criatura no tiene fragmento compatible en el inventario.
            ValueError: Si la criatura no puede evolucionar.
        """
        self._validar_jugador()
        criatura = next(
            (c for c in self.jugador.equipo if c.nombre == nombre_criatura), None
        )
        if criatura is None:
            raise ValueError(f"Criatura '{nombre_criatura}' no encontrada en el equipo.")

        # Buscar un fragmento compatible en el inventario
        fragmento = None
        for item in self.jugador.inventario:
            if isinstance(item, FragmentoEvolucion):
                puede, _ = criatura.puede_evolucionar(item)
                if puede:
                    fragmento = item
                    break

        if fragmento is None:
            # Intentar determinar qué fragmento necesita para dar mensaje claro
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
        # Consumir el fragmento del inventario
        self.jugador.inventario.remove(fragmento)
        return msg

    def set_criatura_combate(self, nombre_criatura: str) -> None:
        """Marca la criatura que el jugador eligió para el combate."""
        self._validar_jugador()
        self.jugador.set_criatura_combate(nombre_criatura)

    def liberar_criatura(self, nombre_criatura: str) -> str:
        """
        Elimina una criatura del equipo de forma voluntaria.

        Retorna:
            str: Mensaje de confirmación.
        """
        self._validar_jugador()
        self.jugador.remover_criatura(nombre_criatura)
        return f"{nombre_criatura} ha sido liberado del equipo."

    def habilidades_criatura_activa(self) -> list[dict]:
        """
        Retorna las habilidades de la criatura activa del jugador en formato dict.
        """
        self._validar_jugador()
        criatura = self.jugador.criatura_activa()
        if criatura is None:
            return []
        return [
            {
                "nombre":      h.nombre,
                "tipo":        h.tipo,
                "costo_mp":    h.costo_mp,
                "potencia":    h.potencia,
                "descripcion": h.descripcion,
                "icono":       h.icono,
                "puede_usar":  criatura.mp >= h.costo_mp,
            }
            for h in criatura.habilidades
        ]

    # ─────────────────────────────────────────
    # RF7 — CONSULTAR EQUIPO E INVENTARIO
    # ─────────────────────────────────────────

    def estado_equipo(self) -> list[dict]:
        self._validar_jugador()
        resultado = []
        for c in self.jugador.equipo:
            resultado.append({
                "nombre":       c.nombre,
                "tipo":         c.tipo.nombre,
                "nivel":        c.nivel,
                "hp":           c.hp,
                "hp_max":       c.hp_max,
                "mp":           c.mp,
                "mp_max":       c.mp_max,
                "atk":          c.atk,
                "defensa":      c.defensa,
                "velocidad":    c.velocidad,
                "experiencia":  c.experiencia,
                "xp_siguiente": c.xp_siguiente,
                "item_equipado": c.item_equipado.nombre if c.item_equipado else "Ninguno",
                "debilitada":   c.esta_debilitada(),
                "forma":        c.forma,
                "habilidades":  [h.nombre for h in c.habilidades],
            })
        return resultado

    def estado_inventario(self) -> list[dict]:
        """
        Retorna ítems e incluye FragmentoEvolucion como tipo especial.
        """
        self._validar_jugador()
        resultado = []
        for i in self.jugador.inventario:
            if isinstance(i, FragmentoEvolucion):
                resultado.append({
                    "nombre":         i.nombre,
                    "descripcion":    i.descripcion,
                    "es_consumible":  True,
                    "es_captura":     False,
                    "es_fragmento":   True,
                    "efecto_positivo": {},
                    "efecto_negativo": {},
                    "icono":          i.icono,
                    "tipo_criatura":  i.tipo_criatura,
                })
            else:
                resultado.append({
                    "nombre":         i.nombre,
                    "descripcion":    i.descripcion,
                    "es_consumible":  i.es_consumible,
                    "es_captura":     i.es_captura,
                    "es_fragmento":   False,
                    "efecto_positivo": i.efecto_positivo,
                    "efecto_negativo": i.efecto_negativo,
                })
        return resultado

    def items_captura_disponibles(self) -> list[str]:
        self._validar_jugador()
        return [
            i.nombre for i in self.jugador.inventario
            if hasattr(i, "es_captura") and i.es_captura
        ]

    def info_zona_actual(self) -> dict:
        self._validar_jugador()
        zona = self.mapa.obtener_zona(self.jugador.posicion)
        tiene_fragmento = _ZONA_FRAGMENTO.get(zona.nombre) is not None
        return {
            "nombre":            zona.nombre,
            "clima_base":        zona.clima_base,
            "criaturas_salvajes": zona.criaturas_salvajes,
            "conexiones":        zona.conexiones,
            "mini_mapa":         self.mini_mapa(),
            "fragmento_zona":    _ZONA_FRAGMENTO.get(zona.nombre),
            "tiene_fragmento":   tiene_fragmento,
        }

    # ─────────────────────────────────────────
    # RF10 — GUARDAR Y CARGAR PARTIDA
    # ─────────────────────────────────────────

    def guardar_partida(self, ruta: str | None = None) -> str:
        ruta = ruta or ruta_partida_default()
        self._validar_jugador()
        self.jugador.guardar(ruta)
        return f"Partida guardada en '{ruta}'."

    def cargar_partida(self, ruta: str | None = None) -> str:
        ruta = ruta or ruta_partida_default()
        self.jugador = Jugador.cargar(ruta)
        self.batalla_activa = None
        self.criatura_encontrada = None
        return (
            f"Partida cargada. Bienvenido de nuevo, {self.jugador.nombre}. "
            f"Estás en {self.jugador.posicion}."
        )

    # ─────────────────────────────────────────
    # UTILIDADES INTERNAS
    # ─────────────────────────────────────────

    def _validar_jugador(self) -> None:
        if self.jugador is None:
            raise RuntimeError("No hay jugador creado. Llama a crear_jugador() primero.")

    def hay_partida_guardada(self, ruta: str | None = None) -> bool:
        ruta = ruta or ruta_partida_default()
        return os.path.isfile(ruta)
#POR FIIIIIIIIIIIIIIIIIIIIIIIIIIIIN 
