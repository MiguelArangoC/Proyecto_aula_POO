"""
game_state.py
=============
Backend del juego de Criaturas por Turnos.
Expone la clase Juego que orquesta todos los módulos: Jugador, Mapa,
Batalla, ítems y persistencia. La interfaz gráfica (GUI) solo llama
métodos de esta clase; nunca accede directamente al modelo.

Uso típico desde la GUI:
    juego = Juego()
    juego.crear_jugador("Ash")
    resultado = juego.mover("norte")
    resultado = juego.iniciar_batalla()
    resultado = juego.ejecutar_turno()
"""

from __future__ import annotations
import random
from typing import Optional

from criatura import Criatura
from jugador import Jugador
from mapa import Mapa
from batalla import Batalla, EstadoBatalla
from item import Item
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

    Atributos:
        jugador (Optional[Jugador]): El jugador activo (None hasta crear_jugador).
        mapa (Mapa): El mapa del mundo con todas las zonas.
        batalla_activa (Optional[Batalla]): Batalla en curso (None si no hay combate).
        criatura_encontrada (Optional[Criatura]): Criatura salvaje del encuentro actual.
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
        """
        Crea un nuevo jugador con una criatura inicial (Ignis) y dos ítems de inicio.

        Parámetros:
            nombre (str): Nombre del jugador.

        Retorna:
            str: Mensaje de confirmación.

        Lanza:
            ValueError: Si el nombre está vacío.
        """
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
        """
        Retorna el nombre de la zona donde se encuentra el jugador.

        Retorna:
            str: Nombre de la zona actual.

        Lanza:
            RuntimeError: Si no hay jugador creado.
        """
        self._validar_jugador()
        return self.jugador.posicion

    def obtener_conexiones(self) -> dict[str, str]:
        """
        Retorna las zonas accesibles desde la posición actual.

        Retorna:
            dict[str, str]: {dirección: nombre_zona_destino}

        Lanza:
            RuntimeError: Si no hay jugador creado.
        """
        self._validar_jugador()
        return self.mapa.zonas_adyacentes(self.jugador.posicion)

    def mover(self, direccion: str) -> str:
        """
        Mueve al jugador en la dirección indicada.

        Parámetros:
            direccion (str): Dirección de movimiento (ej. 'norte').

        Retorna:
            str: Mensaje describiendo el movimiento.

        Lanza:
            RuntimeError: Si no hay jugador.
            ValueError: Si la dirección no es válida desde la zona actual.
        """
        self._validar_jugador()
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
        """Retorna un mini mapa textual con la posición actual del jugador."""
        self._validar_jugador()
        zonas = ["Volcán", "Pradera", "Lago"]
        marcas = {z: ("[X]" if z == self.jugador.posicion else "[ ]") for z in zonas}
        return (
            "Mini mapa:\n"
            f"  {marcas['Volcán']} Volcán\n"
            f"      |\n"
            f"  {marcas['Pradera']} Pradera -- {marcas['Lago']} Lago"
        )

    # ─────────────────────────────────────────
    # RF4 / RF5 — INICIAR BATALLA Y TURNO
    # ─────────────────────────────────────────

    def explorar(self) -> str:
        """
        Intenta generar un encuentro con una criatura salvaje en la zona actual.
        Probabilidad de encuentro: 60%.

        Retorna:
            str: Mensaje indicando si hubo encuentro o no.

        Lanza:
            RuntimeError: Si no hay jugador o ya hay una batalla activa.
        """
        self._validar_jugador()
        if self.batalla_activa and self.batalla_activa.estado == EstadoBatalla.EN_CURSO:
            raise RuntimeError("Ya hay una batalla en curso.")

        if random.random() >= 0.60:
            return "Exploraste la zona pero no encontraste nada."

        zona = self.mapa.obtener_zona(self.jugador.posicion)
        nombre_criatura = zona.obtener_criatura_aleatoria()
        if not nombre_criatura:
            return "Esta zona no tiene criaturas salvajes."

        self.criatura_encontrada = _crear_criatura(nombre_criatura)
        return f"¡Apareció un {nombre_criatura} salvaje!"

    def iniciar_batalla(self) -> str:
        """
        Inicia una batalla contra la criatura encontrada en la exploración.

        Retorna:
            str: El primer mensaje del log de la batalla.

        Lanza:
            RuntimeError: Si no hay criatura encontrada o no hay jugador.
            CriaturaDebilitadaError: Si todas las criaturas del jugador están debilitadas.
        """
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

    def ejecutar_turno(self, usar_item: bool = False, nombre_item: str = "") -> dict:
        """
        Ejecuta un turno de la batalla activa.

        Parámetros:
            usar_item (bool): Si True, se equipa el ítem indicado antes del turno.
            nombre_item (str): Nombre del ítem a equipar (requerido si usar_item=True).

        Retorna:
            dict: {
                "estado": str (nombre del EstadoBatalla),
                "log": list[str] (eventos de este turno),
                "resumen": str (estado actual de la batalla),
            }

        Lanza:
            RuntimeError: Si no hay batalla activa.
            ItemNoDisponibleError: Si el ítem no está en el inventario.
        """
        if self.batalla_activa is None:
            raise RuntimeError("No hay batalla activa.")

        log_antes = len(self.batalla_activa.log)
        estado = self.batalla_activa.ejecutar_turno(usar_item=usar_item, nombre_item=nombre_item)
        nuevos_eventos = self.batalla_activa.log[log_antes:]

        if estado != EstadoBatalla.EN_CURSO:
            self.criatura_encontrada = None

        return {
            "estado": estado.name,
            "log": nuevos_eventos,
            "resumen": self.batalla_activa.resumen(),
        }

    def retirarse(self) -> str:
        """
        Retira al jugador de la batalla actual.

        Retorna:
            str: Mensaje de retirada.

        Lanza:
            RuntimeError: Si no hay batalla activa.
        """
        if self.batalla_activa is None:
            raise RuntimeError("No hay batalla activa.")
        self.batalla_activa.retirarse()
        self.criatura_encontrada = None
        return f"{self.jugador.nombre} se retiró de la batalla."

    def hay_batalla_activa(self) -> bool:
        """Retorna True si hay una batalla en curso."""
        return (
            self.batalla_activa is not None
            and self.batalla_activa.estado == EstadoBatalla.EN_CURSO
        )

    def hay_criatura_encontrada(self) -> bool:
        """Retorna True si hay una criatura encontrada pendiente de batalla o captura."""
        return self.criatura_encontrada is not None

    # ─────────────────────────────────────────
    # RF3 — CAPTURAR CRIATURA
    # ─────────────────────────────────────────

    def capturar(self, nombre_item_captura: str) -> str:
        """
        Intenta capturar la criatura encontrada con un ítem de captura.

        Parámetros:
            nombre_item_captura (str): Nombre del ítem de captura del inventario.

        Retorna:
            str: Mensaje indicando éxito o fallo de la captura.

        Lanza:
            RuntimeError: Si no hay criatura encontrada.
            ItemNoDisponibleError: Si el ítem no está en el inventario.
            EquipoLlenoError: Si el equipo ya tiene 6 criaturas.
            CapturaFallidaError: Si la captura falla por probabilidad.
        """
        self._validar_jugador()
        if self.criatura_encontrada is None:
            raise RuntimeError("No hay criatura salvaje para capturar.")

        try:
            self.jugador.capturar_criatura(self.criatura_encontrada, nombre_item_captura)
            nombre = self.criatura_encontrada.nombre
            self.criatura_encontrada = None
            return f"¡{nombre} fue capturado y se unió a tu equipo!"
        except CapturaFallidaError as e:
            self.criatura_encontrada = None
            raise

    # ─────────────────────────────────────────
    # RF6 — EQUIPAR ÍTEM
    # ─────────────────────────────────────────

    def equipar_item(self, indice_criatura: int, nombre_item: str) -> str:
        """
        Equipa un ítem a una criatura del equipo del jugador.

        Parámetros:
            indice_criatura (int): Posición (0-based) de la criatura en el equipo.
            nombre_item (str): Nombre del ítem del inventario.

        Retorna:
            str: Mensaje de confirmación.

        Lanza:
            RuntimeError: Si no hay jugador.
            IndexError: Si el índice de criatura es inválido.
            ItemNoDisponibleError: Si el ítem no está en el inventario.
            CriaturaDebilitadaError: Si la criatura está debilitada.
        """
        self._validar_jugador()
        if indice_criatura < 0 or indice_criatura >= len(self.jugador.equipo):
            raise IndexError(f"No existe una criatura en la posición {indice_criatura}.")
        criatura = self.jugador.equipo[indice_criatura]
        self.jugador.equipar_item(criatura, nombre_item)
        return f"{nombre_item} equipado a {criatura.nombre}."

    def agregar_item_inventario(self, nombre_item: str) -> str:
        """
        Agrega un ítem del catálogo al inventario del jugador.
        (Útil para pruebas o tiendas futuras.)

        Parámetros:
            nombre_item (str): Nombre del ítem a agregar.

        Retorna:
            str: Mensaje de confirmación.

        Lanza:
            KeyError: Si el ítem no existe en el catálogo.
        """
        self._validar_jugador()
        if nombre_item not in CATALOGO_ITEMS:
            raise KeyError(f"'{nombre_item}' no existe en el catálogo de ítems.")
        self.jugador.agregar_item(_crear_item(nombre_item))
        return f"{nombre_item} agregado al inventario."

    # ─────────────────────────────────────────
    # RF7 — CONSULTAR EQUIPO E INVENTARIO
    # ─────────────────────────────────────────

    def estado_equipo(self) -> list[dict]:
        """
        Retorna la información del equipo del jugador como lista de diccionarios.

        Retorna:
            list[dict]: Una entrada por criatura con sus estadísticas actuales.
        """
        self._validar_jugador()
        resultado = []
        for c in self.jugador.equipo:
            resultado.append({
                "nombre": c.nombre,
                "tipo": c.tipo.nombre,
                "nivel": c.nivel,
                "hp": c.hp,
                "hp_max": c.hp_max,
                "atk": c.atk,
                "defensa": c.defensa,
                "velocidad": c.velocidad,
                "experiencia": c.experiencia,
                "xp_siguiente": c.xp_siguiente,
                "item_equipado": c.item_equipado.nombre if c.item_equipado else "Ninguno",
                "debilitada": c.esta_debilitada(),
            })
        return resultado

    def estado_inventario(self) -> list[dict]:
        """
        Retorna la información del inventario del jugador.

        Retorna:
            list[dict]: Una entrada por ítem con nombre, descripción y tipo.
        """
        self._validar_jugador()
        return [
            {
                "nombre": i.nombre,
                "descripcion": i.descripcion,
                "es_consumible": i.es_consumible,
                "es_captura": i.es_captura,
                "efecto_positivo": i.efecto_positivo,
                "efecto_negativo": i.efecto_negativo,
            }
            for i in self.jugador.inventario
        ]

    def items_captura_disponibles(self) -> list[str]:
        """
        Retorna los nombres de los ítems de captura en el inventario.

        Retorna:
            list[str]: Nombres de ítems con es_captura=True.
        """
        self._validar_jugador()
        return [i.nombre for i in self.jugador.inventario if i.es_captura]

    def info_zona_actual(self) -> dict:
        """
        Retorna información de la zona donde está el jugador.

        Retorna:
            dict: nombre, clima_base, criaturas_salvajes, conexiones.
        """
        self._validar_jugador()
        zona = self.mapa.obtener_zona(self.jugador.posicion)
        return {
            "nombre": zona.nombre,
            "clima_base": zona.clima_base,
            "criaturas_salvajes": zona.criaturas_salvajes,
            "conexiones": zona.conexiones,
            "mini_mapa": self.mini_mapa(),
        }

    # ─────────────────────────────────────────
    # RF10 — GUARDAR Y CARGAR PARTIDA
    # ─────────────────────────────────────────

    def guardar_partida(self, ruta: str = "partida.json") -> str:
        """
        Guarda el estado actual del jugador en un archivo JSON.

        Parámetros:
            ruta (str): Ruta del archivo de guardado.

        Retorna:
            str: Mensaje de confirmación.

        Lanza:
            RuntimeError: Si no hay jugador creado.
            OSError: Si no se puede escribir el archivo.
        """
        self._validar_jugador()
        self.jugador.guardar(ruta)
        return f"Partida guardada en '{ruta}'."

    def cargar_partida(self, ruta: str = "partida.json") -> str:
        """
        Carga una partida guardada y restaura el estado del jugador.

        Parámetros:
            ruta (str): Ruta del archivo de guardado.

        Retorna:
            str: Mensaje de confirmación con nombre y posición restaurados.

        Lanza:
            PartidaNoEncontradaError: Si el archivo no existe.
        """
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
        """
        Verifica que exista un jugador activo.

        Lanza:
            RuntimeError: Si no se ha creado un jugador todavía.
        """
        if self.jugador is None:
            raise RuntimeError("No hay jugador creado. Llama a crear_jugador() primero.")

    def hay_partida_guardada(self, ruta: str = "partida.json") -> bool:
        """
        Verifica si existe un archivo de partida guardada en la ruta dada.

        Parámetros:
            ruta (str): Ruta a verificar.

        Retorna:
            bool: True si el archivo existe.
        """
        import os
        return os.path.isfile(ruta)


# ─────────────────────────────────────────
# DEMO EN CONSOLA (para probar sin GUI)
# ─────────────────────────────────────────

def _menu(opciones: list[str]) -> int:
    """Muestra un menú numerado y retorna la opción elegida (1-based)."""
    for i, op in enumerate(opciones, 1):
        print(f"  [{i}] {op}")
    while True:
        try:
            elec = int(input("Opción: "))
            if 1 <= elec <= len(opciones):
                return elec
        except (ValueError, EOFError):
            pass


def main() -> None:
    """Punto de entrada para prueba en consola."""
    juego = Juego()

    # Inicio: cargar o nueva partida
    if juego.hay_partida_guardada():
        print("Se encontró una partida guardada.")
        op = _menu(["Continuar partida guardada", "Nueva partida"])
        if op == 1:
            print(juego.cargar_partida())
        else:
            nombre = input("Nombre del jugador: ").strip() or "Ash"
            print(juego.crear_jugador(nombre))
    else:
        nombre = input("Nombre del jugador: ").strip() or "Ash"
        print(juego.crear_jugador(nombre))

    # Bucle principal
    while True:
        zona = juego.info_zona_actual()
        print(f"\n=== {zona['nombre']} [{zona['clima_base']}] ===")
        print(f"Jugador: {juego.jugador}")

        op = _menu(["Mover", "Explorar", "Ver equipo", "Ver inventario", "Guardar", "Salir"])

        if op == 1:  # Mover
            conexiones = juego.obtener_conexiones()
            if not conexiones:
                print("No hay salidas disponibles desde aquí.")
                continue
            dirs = list(conexiones.keys())
            print("¿Hacia dónde?")
            elec = _menu([f"{d} → {conexiones[d]}" for d in dirs])
            try:
                print(juego.mover(dirs[elec - 1]))
            except ValueError as e:
                print(f"Error: {e}")

        elif op == 2:  # Explorar
            try:
                msg = juego.explorar()
                print(msg)
                if not juego.hay_criatura_encontrada():
                    continue

                # Encontró criatura: batallar o capturar
                accion = _menu(["Batallar", "Capturar", "Huir"])
                if accion == 1:
                    print(juego.iniciar_batalla())
                    while juego.hay_batalla_activa():
                        print(f"\n{juego.batalla_activa.resumen()}")
                        turno_op = _menu(["Atacar", "Usar ítem", "Retirarse"])
                        if turno_op == 1:
                            resultado = juego.ejecutar_turno()
                        elif turno_op == 2:
                            inv = juego.estado_inventario()
                            if not inv:
                                print("Sin ítems.")
                                resultado = juego.ejecutar_turno()
                            else:
                                print("¿Qué ítem usar?")
                                ei = _menu([i["nombre"] for i in inv])
                                resultado = juego.ejecutar_turno(
                                    usar_item=True,
                                    nombre_item=inv[ei - 1]["nombre"],
                                )
                        else:
                            print(juego.retirarse())
                            break
                        for evento in resultado["log"]:
                            print(" ", evento)
                        if resultado["estado"] != "EN_CURSO":
                            print(f"\n--- {resultado['estado']} ---")
                            break

                elif accion == 2:
                    items_cap = juego.items_captura_disponibles()
                    if not items_cap:
                        print("No tienes ítems de captura.")
                    else:
                        print("¿Qué trampa usar?")
                        ei = _menu(items_cap)
                        try:
                            print(juego.capturar(items_cap[ei - 1]))
                        except CapturaFallidaError as e:
                            print(f"Captura fallida: {e}")
                        except EquipoLlenoError as e:
                            print(f"Equipo lleno: {e}")
                else:
                    juego.criatura_encontrada = None
                    print("Huiste.")

            except RuntimeError as e:
                print(f"Error: {e}")

        elif op == 3:  # Ver equipo
            equipo = juego.estado_equipo()
            if not equipo:
                print("Sin criaturas en el equipo.")
            for c in equipo:
                estado = "✗ DEBILITADA" if c["debilitada"] else "✓"
                print(
                    f"  {estado} {c['nombre']} (Nv.{c['nivel']} | {c['tipo']}) "
                    f"HP:{c['hp']}/{c['hp_max']} ATK:{c['atk']} DEF:{c['defensa']} "
                    f"VEL:{c['velocidad']} XP:{c['experiencia']}/{c['xp_siguiente']} "
                    f"Ítem:{c['item_equipado']}"
                )

        elif op == 4:  # Ver inventario
            inv = juego.estado_inventario()
            if not inv:
                print("Inventario vacío.")
            for item in inv:
                tipo = "Captura" if item["es_captura"] else ("Consumible" if item["es_consumible"] else "Equipable")
                print(f"  [{tipo}] {item['nombre']}: {item['descripcion']}")

        elif op == 5:  # Guardar
            try:
                print(juego.guardar_partida())
            except OSError as e:
                print(f"Error al guardar: {e}")

        else:  # Salir
            print("¡Hasta la próxima!")
            break


if __name__ == "__main__":
    main()
