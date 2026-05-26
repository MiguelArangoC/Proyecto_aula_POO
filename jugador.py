"""
jugador.py
==========
Define la clase Jugador, que representa al usuario dentro del juego.
Gestiona el equipo de criaturas, el inventario de ítems y la posición en el mapa.
"""

import json
from excepciones import EquipoLlenoError, ItemNoDisponibleError, CriaturaDebilitadaError


CAPACIDAD_MAXIMA_EQUIPO = 6


class Jugador:
    """
    Representa al jugador dentro del juego.

    Atributos:
        nombre (str):         Nombre del jugador.
        equipo (list):        Lista de criaturas activas (máx. 6).
        inventario (list):    Lista de ítems y fragmentos disponibles.
        posicion (str):       Nombre de la zona actual en el mapa.
        oro (int):            Monedas del jugador.
        criatura_combate (str): Nombre de la criatura elegida para combatir.
    """

    def __init__(self, nombre, posicion="Pradera", oro=200):
        if not nombre.strip():
            raise ValueError("El nombre del jugador no puede estar vacío.")

        self.nombre           = nombre.strip()
        self.equipo           = []
        self.inventario       = []
        self.posicion         = posicion
        self.oro              = max(0, int(oro))
        self.criatura_combate = None

    # ─────────────────────────────────────────
    # EQUIPO
    # ─────────────────────────────────────────

    def agregar_criatura(self, criatura):
        """
        Agrega una criatura al equipo.
        Lanza EquipoLlenoError si ya tiene 6 criaturas.
        """
        if len(self.equipo) >= CAPACIDAD_MAXIMA_EQUIPO:
            raise EquipoLlenoError(
                f"El equipo de {self.nombre} ya tiene {CAPACIDAD_MAXIMA_EQUIPO} criaturas.",
                CAPACIDAD_MAXIMA_EQUIPO,
            )
        self.equipo.append(criatura)

    def set_criatura_combate(self, nombre):
        """
        Marca la criatura elegida para combatir.
        Lanza ValueError si la criatura no está en el equipo.
        """
        criatura = None
        for c in self.equipo:
            if c.nombre == nombre:
                criatura = c
                break
        if criatura is None:
            raise ValueError(f"Criatura '{nombre}' no encontrada en el equipo.")
        self.criatura_combate = nombre

    def remover_criatura(self, nombre):
        """
        Elimina una criatura del equipo voluntariamente.
        Lanza ValueError si no quedaría al menos una criatura.
        """
        if len(self.equipo) <= 1:
            raise ValueError("Debes conservar al menos una criatura en el equipo.")
        criatura = None
        for c in self.equipo:
            if c.nombre == nombre:
                criatura = c
                break
        if criatura is None:
            raise ValueError(f"Criatura '{nombre}' no encontrada en el equipo.")
        self.equipo.remove(criatura)
        if self.criatura_combate == nombre:
            self.criatura_combate = None

    def criatura_activa(self):
        """
        Retorna la criatura seleccionada para combate si sigue disponible.
        Si no, retorna la primera criatura del equipo que no esté debilitada.
        Retorna None si todas están debilitadas.
        """
        if self.criatura_combate:
            for c in self.equipo:
                if c.nombre == self.criatura_combate and not c.esta_debilitada():
                    return c
        for c in self.equipo:
            if not c.esta_debilitada():
                return c
        return None

    # ─────────────────────────────────────────
    # INVENTARIO
    # ─────────────────────────────────────────

    def agregar_item(self, item):
        """Agrega un ítem al inventario."""
        self.inventario.append(item)

    def tiene_item(self, nombre_item):
        """Retorna True si el ítem con ese nombre está en el inventario."""
        for i in self.inventario:
            if i.nombre == nombre_item:
                return True
        return False

    def obtener_item(self, nombre_item):
        """
        Busca y retorna un ítem del inventario por nombre.
        Lanza ItemNoDisponibleError si no existe.
        """
        for item in self.inventario:
            if item.nombre == nombre_item:
                return item
        raise ItemNoDisponibleError(
            f"'{nombre_item}' no está en el inventario.",
            nombre_item,
        )

    def consumir_item(self, nombre_item):
        """
        Elimina un ítem del inventario.
        Lanza ItemNoDisponibleError si no existe.
        """
        item = self.obtener_item(nombre_item)
        self.inventario.remove(item)

    # ─────────────────────────────────────────
    # EQUIPAR ÍTEM
    # ─────────────────────────────────────────

    def equipar_item(self, criatura, nombre_item):
        """
        Equipa un ítem a una criatura del equipo.
        Si ya tenía un ítem equipado, lo revierte primero.
        """
        if criatura.esta_debilitada():
            raise CriaturaDebilitadaError(
                f"No se puede equipar un ítem a {criatura.nombre}: está debilitada.",
                criatura.nombre,
            )

        nuevo_item = self.obtener_item(nombre_item)

        # Si ya tiene ítem equipado, revertir sus efectos antes de aplicar el nuevo
        if criatura.item_equipado is not None:
            criatura.item_equipado.modificar_estadistica(criatura, revertir=True)

        nuevo_item.modificar_estadistica(criatura, revertir=False)
        criatura.item_equipado = nuevo_item

    # ─────────────────────────────────────────
    # CAPTURA
    # ─────────────────────────────────────────

    def capturar_criatura(self, criatura, nombre_item_captura):
        """
        Intenta capturar una criatura salvaje usando un ítem de captura.
        La probabilidad aumenta cuanto menos HP tiene la criatura.
        El ítem se consume siempre, independientemente del resultado.
        """
        import random
        from excepciones import CapturaFallidaError

        item = self.obtener_item(nombre_item_captura)

        if not item.es_captura:
            raise ItemNoDisponibleError(
                f"'{nombre_item_captura}' no es un ítem de captura.",
                nombre_item_captura,
            )

        # Probabilidad: cuanto menos HP, más fácil capturar
        ratio_hp      = criatura.hp / criatura.hp_max
        probabilidad  = max(0.10, 1.0 - ratio_hp * 0.85)

        self.consumir_item(nombre_item_captura)

        if random.random() > probabilidad:
            raise CapturaFallidaError(
                f"{criatura.nombre} escapó del intento de captura.",
                criatura.nombre,
            )

        self.agregar_criatura(criatura)

    # ─────────────────────────────────────────
    # PERSISTENCIA
    # ─────────────────────────────────────────

    def guardar(self, ruta="partida.json"):
        """Serializa el estado del jugador en un archivo JSON."""
        datos = {
            "nombre":           self.nombre,
            "posicion":         self.posicion,
            "oro":              self.oro,
            "criatura_combate": self.criatura_combate,
            "equipo": [
                {
                    "nombre":    c.nombre,
                    "tipo":      c.tipo.nombre,
                    "hp":        c.hp,
                    "hp_max":    c.hp_max,
                    "mp":        c.mp,
                    "mp_max":    c.mp_max,
                    "atk":       c.atk,
                    "defensa":   c.defensa,
                    "velocidad": c.velocidad,
                    "precision": c.precision,
                    "nivel":     c.nivel,
                    "experiencia":  c.experiencia,
                    "xp_siguiente": c.xp_siguiente,
                    "forma":        c.forma,
                    "habilidades":  [h.nombre for h in c.habilidades],
                    "item_equipado": (
                        {
                            "nombre":          c.item_equipado.nombre,
                            "descripcion":     c.item_equipado.descripcion,
                            "efecto_positivo": c.item_equipado.efecto_positivo,
                            "efecto_negativo": c.item_equipado.efecto_negativo,
                            "es_consumible":   c.item_equipado.es_consumible,
                            "es_captura":      c.item_equipado.es_captura,
                        }
                        if c.item_equipado is not None
                        else None
                    ),
                }
                for c in self.equipo
            ],
            "inventario": [
                {
                    "nombre":          i.nombre,
                    "descripcion":     i.descripcion,
                    "efecto_positivo": i.efecto_positivo,
                    "efecto_negativo": i.efecto_negativo,
                    "es_consumible":   i.es_consumible,
                    "es_captura":      i.es_captura,
                    "es_fragmento":    getattr(i, "es_fragmento", False),
                }
                for i in self.inventario
            ],
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def __repr__(self):
        return (
            f"Jugador(nombre='{self.nombre}', posicion='{self.posicion}', oro={self.oro}, "
            f"criaturas={len(self.equipo)}, items={len(self.inventario)})"
        )

    def __str__(self):
        return (
            f"Jugador: {self.nombre} | Zona: {self.posicion} | "
            f"Criaturas: {len(self.equipo)}/{CAPACIDAD_MAXIMA_EQUIPO} | "
            f"Ítems: {len(self.inventario)} | Oro: {self.oro}"
        )


# ─────────────────────────────────────────
# FUNCIÓN DE CARGA (antes era @classmethod)
# ─────────────────────────────────────────

def cargar_jugador(ruta="partida.json"):
    """
    Carga y reconstruye un Jugador desde un archivo JSON guardado.
    Retorna el objeto Jugador restaurado con su equipo e inventario.
    Lanza PartidaNoEncontradaError si el archivo no existe.
    """
    from excepciones import PartidaNoEncontradaError
    from criatura import Criatura
    from item import Item
    from fragmento import FragmentoEvolucion, CATALOGO_FRAGMENTOS
    from habilidad import CATALOGO_HABILIDADES

    # Intentar abrir el archivo
    try:
        archivo = open(ruta, "r", encoding="utf-8")
        datos   = json.load(archivo)
        archivo.close()
    except FileNotFoundError:
        raise PartidaNoEncontradaError(
            f"No se encontró la partida guardada en '{ruta}'.",
            ruta,
        )

    jugador = Jugador(datos["nombre"], datos["posicion"], datos.get("oro", 0))
    jugador.criatura_combate = datos.get("criatura_combate")

    # Reconstruir equipo
    for cd in datos["equipo"]:
        c = Criatura(
            nombre=cd["nombre"],
            tipo=cd["tipo"],
            hp=cd["hp_max"],
            atk=cd["atk"],
            defensa=cd["defensa"],
            velocidad=cd["velocidad"],
            precision=cd["precision"],
            nivel=cd["nivel"],
            mp_max=cd.get("mp_max", 40),
            forma=cd.get("forma", 0),
        )
        c.hp          = cd["hp"]
        c.mp          = cd.get("mp", c.mp_max)
        c.experiencia = cd["experiencia"]
        c.xp_siguiente = cd["xp_siguiente"]

        if "habilidades" in cd:
            habilidades_recuperadas = []
            for nombre_hab in cd["habilidades"]:
                if nombre_hab in CATALOGO_HABILIDADES:
                    habilidades_recuperadas.append(CATALOGO_HABILIDADES[nombre_hab])
            if habilidades_recuperadas:
                c.habilidades = habilidades_recuperadas
            else:
                c.habilidades = [CATALOGO_HABILIDADES["Atacar"]]

        # Restaurar ítem equipado si existía
        if cd.get("item_equipado") is not None:
            id_ = cd["item_equipado"]
            item_eq = Item(
                nombre=id_["nombre"],
                descripcion=id_["descripcion"],
                efecto_positivo=id_["efecto_positivo"],
                efecto_negativo=id_["efecto_negativo"],
                es_consumible=id_["es_consumible"],
                es_captura=id_["es_captura"],
            )
            c.item_equipado = item_eq

        jugador.equipo.append(c)

    # Reconstruir inventario
    for id_ in datos["inventario"]:
        if id_.get("es_fragmento") or id_["nombre"] in CATALOGO_FRAGMENTOS:
            item = FragmentoEvolucion(id_["nombre"])
        else:
            item = Item(
                nombre=id_["nombre"],
                descripcion=id_["descripcion"],
                efecto_positivo=id_["efecto_positivo"],
                efecto_negativo=id_["efecto_negativo"],
                es_consumible=id_["es_consumible"],
                es_captura=id_["es_captura"],
            )
        jugador.inventario.append(item)

    return jugador
