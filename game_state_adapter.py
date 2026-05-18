"""
game_state_adapter.py
=====================
Adapta la clase Juego (backend real) a la interfaz que espera GUIClaude.py.

La GUI asume un objeto `GameState` con atributos:
  - player_name  (str)
  - gold         (int)
  - creatures    (list[dict])   — formato GUI
  - active_creature (dict|None) — formato GUI
  - inventory    (list[dict])   — formato GUI

Este módulo expone `GameState` como alias de `GameStateAdapter`,
de modo que la GUI sólo necesita cambiar su import a:
    from game_state_adapter import GameState
"""

from __future__ import annotations
from game_state import Juego
from excepciones import (
    EquipoLlenoError, CapturaFallidaError,
    ItemNoDisponibleError, CriaturaDebilitadaError,
    PartidaNoEncontradaError,
)

# ── Iconos y colores por tipo elemental ──────────────────────────────────────
_TIPO_ICON: dict[str, str] = {
    "Fuego":  "🔥",
    "Agua":   "💧",
    "Tierra": "🪨",
    "Rayo":   "⚡",
    "Normal": "⭐",
}
_TIPO_COLOR: dict[str, str] = {
    "Fuego":  "#E67E22",
    "Agua":   "#3498DB",
    "Tierra": "#95A5A6",
    "Rayo":   "#F1C40F",
    "Normal": "#BDC3C7",
}

# ── Ítems de la tienda (estáticos, sin conexión a catálogo) ──────────────────
SHOP_ITEMS = [
    {
        "name": "Poción",
        "desc": "Restaura 30 HP a la criatura equipada.",
        "icon": "🧪",
        "type": "Consumible",
        "price": 50,
    },
    {
        "name": "Amuleto de Fuego",
        "desc": "ATK +10, DEF -5.",
        "icon": "🔮",
        "type": "Accesorio",
        "price": 120,
    },
    {
        "name": "Escudo Terrenal",
        "desc": "DEF +15, VEL -3.",
        "icon": "🛡",
        "type": "Accesorio",
        "price": 100,
    },
    {
        "name": "Trampa Básica",
        "desc": "Permite capturar una criatura salvaje.",
        "icon": "🪤",
        "type": "Consumible",
        "price": 80,
    },
]


def _criatura_a_gui(c: dict) -> dict:
    """Convierte un dict de estado_equipo() al formato que espera la GUI."""
    tipo = c["tipo"]
    return {
        "name":      c["nombre"],
        "type":      tipo,
        "level":     c["nivel"],
        "hp":        c["hp"],
        "max_hp":    c["hp_max"],
        "mp":        0,
        "max_mp":    1,   # no existe MP, barra vacía
        "xp":        c["experiencia"],
        "xp_next":   c["xp_siguiente"],
        "atk":       c["atk"],
        "def_":      c["defensa"],
        "spd":       c["velocidad"],
        "icon":      _TIPO_ICON.get(tipo, "❓"),
        "color":     _TIPO_COLOR.get(tipo, "#FFFFFF"),
        "status":    "Debilitada" if c["debilitada"] else None,
        "skills":    ["Atacar"],   # acción básica siempre disponible
        "item":      c["item_equipado"],
        # referencia al índice para equipar ítems
        "_backend_nombre": c["nombre"],
    }


def _item_a_gui(i: dict, qty: int = 1) -> dict:
    """Convierte un dict de estado_inventario() al formato que espera la GUI."""
    if i["es_captura"]:
        tipo = "Consumible"
        icon = "🪤"
    elif i["es_consumible"]:
        tipo = "Consumible"
        icon = "🧪"
    else:
        tipo = "Accesorio"
        icon = "🔮"

    efectos_pos = ", ".join(f"+{v} {k}" for k, v in i["efecto_positivo"].items())
    efectos_neg = ", ".join(f"-{v} {k}" for k, v in i["efecto_negativo"].items())
    desc_extra = " | ".join(filter(None, [efectos_pos, efectos_neg]))
    desc = i["descripcion"]
    if desc_extra:
        desc = f"{desc} ({desc_extra})"

    return {
        "name":        i["nombre"],
        "desc":        desc,
        "icon":        icon,
        "type":        tipo,
        "qty":         qty,
        "price":       0,    # precio desconocido desde backend
        # referencia al nombre original para usar en backend
        "_backend_nombre": i["nombre"],
    }


class GameStateAdapter:
    """
    Fachada que conecta Juego (backend) con la GUI.

    Expone los atributos que la GUI lee directamente
    (creatures, inventory, active_creature, gold, player_name)
    y los mantiene sincronizados con el backend.
    """

    SHOP_ITEMS = SHOP_ITEMS

    def __init__(self) -> None:
        self.juego: Juego = Juego()
        self.player_name: str = ""
        self.gold: int = 0
        self.active_creature: dict | None = None
        self.creatures: list[dict] = []
        self.inventory: list[dict] = []

    # ── Sincronización ───────────────────────────────────────────────────────

    def sync(self) -> None:
        """Actualiza creatures e inventory desde el backend."""
        if self.juego.jugador is None:
            return

        # Criaturas
        self.creatures = [_criatura_a_gui(c) for c in self.juego.estado_equipo()]

        # Mantener criatura activa apuntando al mismo nombre
        if self.active_creature:
            nombre = self.active_creature.get("_backend_nombre", "")
            nuevo = next((c for c in self.creatures
                          if c["_backend_nombre"] == nombre), None)
            self.active_creature = nuevo or (self.creatures[0] if self.creatures else None)
        elif self.creatures:
            self.active_creature = self.creatures[0]

        # Inventario — agrupar por nombre
        inv_raw = self.juego.estado_inventario()
        conteo: dict[str, int] = {}
        for i in inv_raw:
            conteo[i["nombre"]] = conteo.get(i["nombre"], 0) + 1

        visto: set[str] = set()
        self.inventory = []
        for i in inv_raw:
            if i["nombre"] not in visto:
                visto.add(i["nombre"])
                self.inventory.append(_item_a_gui(i, conteo[i["nombre"]]))

    # ── Acciones del jugador ─────────────────────────────────────────────────

    def crear_jugador(self, nombre: str) -> str:
        """Crea el jugador y sincroniza el estado inicial."""
        msg = self.juego.crear_jugador(nombre)
        self.player_name = nombre
        self.sync()
        return msg

    def cargar_partida(self, ruta: str = "partida.json") -> str:
        """Carga partida guardada y sincroniza."""
        msg = self.juego.cargar_partida(ruta)
        self.player_name = self.juego.jugador.nombre
        self.sync()
        return msg

    def guardar_partida(self, ruta: str = "partida.json") -> str:
        return self.juego.guardar_partida(ruta)

    def hay_partida_guardada(self, ruta: str = "partida.json") -> bool:
        return self.juego.hay_partida_guardada(ruta)

    # ── Exploración ──────────────────────────────────────────────────────────

    def explorar(self) -> str:
        return self.juego.explorar()

    def hay_criatura_encontrada(self) -> bool:
        return self.juego.hay_criatura_encontrada()

    def info_zona_actual(self) -> dict:
        return self.juego.info_zona_actual()

    def obtener_conexiones(self) -> dict:
        return self.juego.obtener_conexiones()

    def mover(self, direccion: str) -> str:
        return self.juego.mover(direccion)

    # ── Combate ──────────────────────────────────────────────────────────────

    def iniciar_batalla(self) -> str:
        return self.juego.iniciar_batalla()

    def ejecutar_turno(self, usar_item: bool = False,
                       nombre_item: str = "") -> dict:
        resultado = self.juego.ejecutar_turno(usar_item=usar_item,
                                               nombre_item=nombre_item)
        self.sync()
        return resultado

    def retirarse(self) -> str:
        msg = self.juego.retirarse()
        self.sync()
        return msg

    def hay_batalla_activa(self) -> bool:
        return self.juego.hay_batalla_activa()

    def criatura_enemiga_gui(self) -> dict | None:
        """Retorna la criatura enemiga en formato GUI (para mostrar en arena)."""
        if self.juego.criatura_encontrada is None and self.juego.batalla_activa is None:
            return None
        ce = None
        if self.juego.batalla_activa:
            ce = self.juego.batalla_activa.enemigo
        elif self.juego.criatura_encontrada:
            ce = self.juego.criatura_encontrada
        if ce is None:
            return None
        tipo = ce.tipo.nombre
        return {
            "name":    ce.nombre,
            "type":    tipo,
            "hp":      ce.hp,
            "max_hp":  ce.hp_max,
            "atk":     ce.atk,
            "icon":    _TIPO_ICON.get(tipo, "❓"),
            "color":   _TIPO_COLOR.get(tipo, "#FFFFFF"),
            "status":  "Debilitada" if ce.esta_debilitada() else None,
            "skills":  [],
        }

    def clima_batalla_actual(self) -> str:
        """Retorna el nombre del clima de la batalla activa."""
        if self.juego.batalla_activa:
            return self.juego.batalla_activa.condicion_climatica.nombre
        zona = self.juego.mapa.obtener_zona(self.juego.jugador.posicion)
        return zona.clima_base

    # ── Captura ──────────────────────────────────────────────────────────────

    def capturar(self, nombre_item: str) -> str:
        msg = self.juego.capturar(nombre_item)
        self.sync()
        return msg

    def items_captura_disponibles(self) -> list[str]:
        return self.juego.items_captura_disponibles()

    # ── Ítems / equipo ───────────────────────────────────────────────────────

    def equipar_item(self, nombre_criatura: str, nombre_item: str) -> str:
        """Equipa ítem a la criatura con el nombre dado."""
        idx = next((i for i, c in enumerate(self.juego.jugador.equipo)
                    if c.nombre == nombre_criatura), None)
        if idx is None:
            raise ValueError(f"Criatura '{nombre_criatura}' no encontrada.")
        msg = self.juego.equipar_item(idx, nombre_item)
        self.sync()
        return msg

    def agregar_item_inventario(self, nombre_item: str) -> str:
        msg = self.juego.agregar_item_inventario(nombre_item)
        self.sync()
        return msg

    def set_active_creature(self, creature_gui: dict) -> None:
        """Marca como criatura activa la indicada por dict GUI."""
        self.active_creature = creature_gui


# Alias para que la GUI sólo cambie el import
GameState = GameStateAdapter
