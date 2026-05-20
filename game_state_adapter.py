"""
game_state_adapter.py
=====================
Adapta la clase Juego (backend real) a la interfaz que espera GUIClaude.py.

Cambios en esta versión
-----------------------
  - cruzar_criaturas(): invoca cruza.cruzar() y agrega el hijo al equipo.
  - combinaciones_cruza(): expone la tabla completa para el panel de cruzas.
  - _criatura_a_gui() soporta criaturas de cruza (_es_cruza, _tipo_cruza, etc.).
  - estado_inventario() incluye fragmentos en el inventario GUI.
  - ejecutar_turno() pasa nombre_habilidad al backend.
  - habilidades_criatura_activa(): expone habilidades reales con estado de MP.
"""

from __future__ import annotations
from game_state import Juego, CATALOGO_ITEMS, _crear_item
from excepciones import (
    EquipoLlenoError, CapturaFallidaError,
    ItemNoDisponibleError, CriaturaDebilitadaError,
    PartidaNoEncontradaError,
)
from cruza import cruzar, combinaciones_disponibles, ResultadoCruza

# ── Iconos y colores por tipo elemental ──────────────────────────────────────
_TIPO_ICON: dict[str, str] = {
    "Fuego":  "🔥",
    "Agua":   "💧",
    "Tierra": "🪨",
    "Rayo":   "⚡",
    "Normal": "⭐",
    "Hielo":  "❄️",
}
_TIPO_COLOR: dict[str, str] = {
    "Fuego":  "#E67E22",
    "Agua":   "#3498DB",
    "Tierra": "#95A5A6",
    "Rayo":   "#F1C40F",
    "Normal": "#BDC3C7",
    "Hielo":  "#AEE8F8",
}

# ── Ítems de la tienda ────────────────────────────────────────────────────────
SHOP_ITEMS = [
    {
        "name":  "Poción",
        "desc":  "Restaura 30 HP a la criatura equipada.",
        "icon":  "🧪",
        "type":  "Consumible",
        "price": 50,
    },
    {
        "name":  "Amuleto de Fuego",
        "desc":  "ATK +10, DEF -5.",
        "icon":  "🔮",
        "type":  "Accesorio",
        "price": 120,
    },
    {
        "name":  "Escudo Terrenal",
        "desc":  "DEF +15, VEL -3.",
        "icon":  "🛡",
        "type":  "Accesorio",
        "price": 100,
    },
    {
        "name":  "Trampa Básica",
        "desc":  "Permite capturar una criatura salvaje.",
        "icon":  "🪤",
        "type":  "Consumible",
        "price": 80,
    },
]


def _criatura_a_gui(c: dict) -> dict:
    """Convierte un dict de estado_equipo() al formato que espera la GUI."""
    tipo = c["tipo"]
    # Criaturas de cruza tienen icono/color especiales
    icono = c.get("icono_cruza") or _TIPO_ICON.get(tipo, "❓")
    color = c.get("color_cruza") or _TIPO_COLOR.get(tipo, "#FFFFFF")
    tipo_display = c.get("tipo_cruza") or tipo

    return {
        "name":             c["nombre"],
        "type":             tipo_display,
        "level":            c["nivel"],
        "hp":               c["hp"],
        "max_hp":           c["hp_max"],
        "mp":               c.get("mp", 0),
        "max_mp":           c.get("mp_max", 1),
        "xp":               c["experiencia"],
        "xp_next":          c["xp_siguiente"],
        "atk":              c["atk"],
        "def_":             c["defensa"],
        "spd":              c["velocidad"],
        "icon":             icono,
        "color":            color,
        "status":           "Debilitada" if c["debilitada"] else None,
        "skills":           c.get("habilidades", ["Atacar"]),
        "item":             c["item_equipado"],
        "es_cruza":         c.get("es_cruza", False),
        "es_mutacion":      c.get("es_mutacion", False),
        "afinidad":         c.get("afinidad", ""),
        "desc_afinidad":    c.get("desc_afinidad", ""),
        "_backend_nombre":  c["nombre"],
    }


def _item_a_gui(i: dict, qty: int = 1) -> dict:
    """Convierte un dict de estado_inventario() al formato que espera la GUI."""
    # Fragmentos de evolución
    if i.get("es_fragmento"):
        return {
            "name":             i["nombre"],
            "desc":             i["descripcion"],
            "icon":             i.get("icono", "🔶"),
            "type":             "Material",
            "qty":              qty,
            "price":            0,
            "es_fragmento":     True,
            "_backend_nombre":  i["nombre"],
        }

    if i.get("es_captura"):
        tipo = "Consumible"
        icon = "🪤"
    elif i.get("es_consumible"):
        tipo = "Consumible"
        icon = "🧪"
    else:
        tipo = "Accesorio"
        icon = "🔮"

    efectos_pos = ", ".join(f"+{v} {k}" for k, v in i.get("efecto_positivo", {}).items())
    efectos_neg = ", ".join(f"-{v} {k}" for k, v in i.get("efecto_negativo", {}).items())
    desc_extra  = " | ".join(filter(None, [efectos_pos, efectos_neg]))
    desc = i["descripcion"]
    if desc_extra:
        desc = f"{desc} ({desc_extra})"

    return {
        "name":             i["nombre"],
        "desc":             desc,
        "icon":             icon,
        "type":             tipo,
        "qty":              qty,
        "price":            0,
        "es_fragmento":     False,
        "_backend_nombre":  i["nombre"],
    }


class GameStateAdapter:
    """
    Fachada que conecta Juego (backend) con la GUI.
    """

    SHOP_ITEMS = SHOP_ITEMS

    def __init__(self) -> None:
        self.juego: Juego           = Juego()
        self.player_name: str       = ""
        self.gold: int              = 0
        self.active_creature: dict | None = None
        self.creatures: list[dict]  = []
        self.inventory: list[dict]  = []
        # Cache de habilidades de la criatura activa (actualizado en sync)
        self.active_skills: list[dict] = []

    # ── Sincronización ───────────────────────────────────────────────────────

    def sync(self) -> None:
        """Actualiza creatures, inventory y active_skills desde el backend."""
        if self.juego.jugador is None:
            return

        self.gold = self.juego.jugador.oro

        # Criaturas — incluye datos extra para cruzas
        equipo_raw = self.juego.estado_equipo()
        # Enriquecer dicts con metadata de cruza si aplica
        for i, c_obj in enumerate(self.juego.jugador.equipo):
            if getattr(c_obj, "_es_cruza", False):
                equipo_raw[i]["es_cruza"]     = True
                equipo_raw[i]["es_mutacion"]  = getattr(c_obj, "_es_mutacion", False)
                equipo_raw[i]["tipo_cruza"]   = getattr(c_obj, "_tipo_cruza", "")
                equipo_raw[i]["icono_cruza"]  = getattr(c_obj, "_icono_cruza", "")
                equipo_raw[i]["color_cruza"]  = getattr(c_obj, "_color_cruza", "")
                equipo_raw[i]["afinidad"]     = getattr(c_obj, "_afinidad", "")
                equipo_raw[i]["desc_afinidad"]= getattr(c_obj, "_desc_afinidad", "")

        self.creatures = [_criatura_a_gui(c) for c in equipo_raw]

        # Mantener criatura activa y sincronizar selección con el backend
        if self.active_creature:
            nombre = self.active_creature.get("_backend_nombre", "")
            nuevo = next(
                (c for c in self.creatures if c["_backend_nombre"] == nombre), None
            )
            self.active_creature = nuevo or (self.creatures[0] if self.creatures else None)
        elif self.creatures:
            self.active_creature = self.creatures[0]

        if self.active_creature:
            self.juego.set_criatura_combate(
                self.active_creature["_backend_nombre"]
            )

        # Inventario agrupado por nombre
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

        # Habilidades de la criatura activa
        self.active_skills = self.juego.habilidades_criatura_activa()

    # ── Acciones del jugador ─────────────────────────────────────────────────

    def crear_jugador(
        self, nombre: str, criatura_inicial: str = "Ignis", oro_inicial: int = 200
    ) -> str:
        msg = self.juego.crear_jugador(nombre, criatura_inicial=criatura_inicial,
                                        oro_inicial=oro_inicial)
        self.player_name = nombre
        self.sync()
        return msg

    def cargar_partida(self, ruta: str | None = None) -> str:
        msg = self.juego.cargar_partida(ruta)
        self.player_name = self.juego.jugador.nombre
        self.sync()
        return msg

    def guardar_partida(self, ruta: str | None = None) -> str:
        return self.juego.guardar_partida(ruta)

    def hay_partida_guardada(self, ruta: str | None = None) -> bool:
        return self.juego.hay_partida_guardada(ruta)

    # ── Exploración ──────────────────────────────────────────────────────────

    def explorar(self) -> str:
        msg = self.juego.explorar()
        self.sync()   # sync para reflejar posible fragmento en inventario
        return msg

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

    def ejecutar_turno(
        self,
        usar_item: bool = False,
        nombre_item: str = "",
        nombre_habilidad: str = "",
    ) -> dict:
        resultado = self.juego.ejecutar_turno(
            usar_item=usar_item,
            nombre_item=nombre_item,
            nombre_habilidad=nombre_habilidad,
        )
        self.sync()
        return resultado

    def retirarse(self) -> str:
        msg = self.juego.retirarse()
        self.sync()
        return msg

    def hay_batalla_activa(self) -> bool:
        return self.juego.hay_batalla_activa()

    def criatura_enemiga_gui(self) -> dict | None:
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
        if self.juego.batalla_activa:
            return self.juego.batalla_activa.condicion_climatica.nombre
        zona = self.juego.mapa.obtener_zona(self.juego.jugador.posicion)
        return zona.clima_base

    # ── Captura ──────────────────────────────────────────────────────────────

    def capturar(self, nombre_item: str) -> str:
        msg = self.juego.capturar(nombre_item)
        self.sync()
        return msg

    def intentar_captura_en_batalla(self, nombre_item: str) -> dict:
        if not self.juego.batalla_activa:
            raise RuntimeError("No hay batalla activa.")
        log_antes = len(self.juego.batalla_activa.log)
        
        exito = False
        msg = ""
        try:
            msg = self.juego.intentar_captura_en_batalla(nombre_item)
            exito = True
            nuevos_eventos = [msg]
            estado_nombre = "VICTORIA"
        except CapturaFallidaError as e:
            exito = False
            msg = str(e)
            nuevos_eventos = self.juego.batalla_activa.log[log_antes:]
            estado_nombre = self.juego.batalla_activa.estado.name
        
        self.sync()
        return {
            "exito": exito,
            "mensaje": msg,
            "log": nuevos_eventos,
            "estado": estado_nombre
        }

    def items_captura_disponibles(self) -> list[str]:
        return self.juego.items_captura_disponibles()

    # ── Ítems / equipo ───────────────────────────────────────────────────────

    def equipar_item(self, nombre_criatura: str, nombre_item: str) -> str:
        idx = next(
            (i for i, c in enumerate(self.juego.jugador.equipo)
             if c.nombre == nombre_criatura),
            None,
        )
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
        self.active_creature = creature_gui
        nombre = creature_gui.get("_backend_nombre", "")
        if nombre:
            self.juego.set_criatura_combate(nombre)
        self.active_skills = self.juego.habilidades_criatura_activa()

    def liberar_criatura(self, nombre_criatura: str) -> str:
        """Elimina una criatura del equipo y actualiza el estado de la GUI."""
        if (
            self.active_creature
            and self.active_creature.get("_backend_nombre") == nombre_criatura
        ):
            self.active_creature = None
        msg = self.juego.liberar_criatura(nombre_criatura)
        self.sync()
        return msg

    # ── Habilidades ──────────────────────────────────────────────────────────

    def habilidades_criatura_activa(self) -> list[dict]:
        """Habilidades de la criatura activa con estado de MP."""
        return self.juego.habilidades_criatura_activa()

    # ── Evolución ────────────────────────────────────────────────────────────

    def evolucionar_criatura(self, nombre_criatura: str) -> str:
        msg = self.juego.evolucionar_criatura(nombre_criatura)
        self.sync()
        return msg

    # ── Cruzas ───────────────────────────────────────────────────────────────

    def cruzar_criaturas(self, nombre_a: str, nombre_b: str) -> str:
        """
        Cruza dos criaturas del equipo del jugador.

        Retorna el mensaje descriptivo del resultado.

        Lanza:
            ValueError: Si no se encuentra alguna criatura o la combinación no existe.
            EquipoLlenoError: Si el equipo ya tiene 6 criaturas.
        """
        jugador = self.juego.jugador
        if jugador is None:
            raise RuntimeError("No hay jugador activo.")

        padre_a = next((c for c in jugador.equipo if c.nombre == nombre_a), None)
        padre_b = next((c for c in jugador.equipo if c.nombre == nombre_b), None)

        if padre_a is None:
            raise ValueError(f"Criatura '{nombre_a}' no encontrada en el equipo.")
        if padre_b is None:
            raise ValueError(f"Criatura '{nombre_b}' no encontrada en el equipo.")
        if padre_a is padre_b:
            raise ValueError("No puedes cruzar una criatura consigo misma.")

        resultado: ResultadoCruza = cruzar(padre_a, padre_b)
        jugador.agregar_criatura(resultado.criatura)
        self.sync()
        return resultado.mensaje

    def combinaciones_cruza(self) -> list[dict]:
        """Retorna la tabla completa de combinaciones posibles."""
        return combinaciones_disponibles()

    def puede_cruzar(self, nombre_a: str, nombre_b: str) -> tuple[bool, str]:
        """
        Verifica si dos criaturas del equipo pueden cruzarse sin hacer la cruza.

        Retorna (True, "") o (False, motivo).
        """
        from cruza import TABLA_CRUZAS
        jugador = self.juego.jugador
        if jugador is None:
            return False, "No hay jugador activo."
        padre_a = next((c for c in jugador.equipo if c.nombre == nombre_a), None)
        padre_b = next((c for c in jugador.equipo if c.nombre == nombre_b), None)
        if padre_a is None or padre_b is None:
            return False, "Una o ambas criaturas no están en el equipo."
        if padre_a is padre_b:
            return False, "No puedes cruzar una criatura consigo misma."
        from frozenset import frozenset  # ya está en builtins
        clave = frozenset({padre_a.tipo.nombre, padre_b.tipo.nombre})
        if clave not in TABLA_CRUZAS:
            return False, (
                f"No existe cruza para {padre_a.tipo.nombre} × {padre_b.tipo.nombre}."
            )
        if len(jugador.equipo) >= 6:
            return False, "El equipo ya tiene 6 criaturas. Libera una primero."
        return True, ""

    # ── Mapa ─────────────────────────────────────────────────────────────────

    def mapa_mundo(self) -> dict[str, dict]:
        return {
            nombre: {
                "nombre":             zona.nombre,
                "clima_base":         zona.clima_base,
                "criaturas_salvajes": list(zona.criaturas_salvajes),
                "conexiones":         dict(zona.conexiones),
            }
            for nombre, zona in self.juego.mapa.zonas.items()
        }

    def mini_mapa(self) -> str:
        return self.juego.mini_mapa()


# Alias para que la GUI sólo cambie el import
GameState = GameStateAdapter