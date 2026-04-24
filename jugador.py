"""
jugador.py
==========
Define la clase Jugador, que representa al usuario dentro del juego.
Gestiona el equipo de criaturas, el inventario de ítems y la posición
en el mapa.
"""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional

from excepciones import (
    EquipoLlenoError,
    ItemNoDisponibleError,
    CriaturaDebilitadaError,
)

if TYPE_CHECKING:
    from criatura import Criatura
    from item import Item


CAPACIDAD_MAXIMA_EQUIPO: int = 6


class Jugador:
    """
    Representa al jugador dentro del juego.

    Atributos:
        nombre (str): Nombre del jugador.
        equipo (list[Criatura]): Lista de criaturas activas (máx. 6).
        inventario (list[Item]): Lista de ítems disponibles.
        posicion (str): Nombre de la zona actual en el mapa.
    """

    def __init__(self, nombre: str, posicion: str = "Pradera") -> None:
        """
        Inicializa un jugador nuevo sin criaturas ni ítems.

        Parámetros:
            nombre (str): Nombre del jugador (no puede estar vacío).
            posicion (str): Zona inicial en el mapa. Por defecto 'Pradera'.

        Lanza:
            ValueError: Si el nombre está vacío o solo tiene espacios en blanco.
        """
        if not nombre.strip():
            raise ValueError("El nombre del jugador no puede estar vacío.")

        self.nombre: str = nombre.strip()
        self.equipo: list["Criatura"] = []
        self.inventario: list["Item"] = []
        self.posicion: str = posicion

    # ─────────────────────────────────────────
    # EQUIPO
    # ─────────────────────────────────────────

    def agregar_criatura(self, criatura: "Criatura") -> None:
        """
        Agrega una criatura al equipo del jugador.

        Parámetros:
            criatura (Criatura): La criatura a agregar.

        Retorna:
            None

        Lanza:
            EquipoLlenoError: Si el equipo ya tiene 6 criaturas.
        """
        if len(self.equipo) >= CAPACIDAD_MAXIMA_EQUIPO:
            raise EquipoLlenoError(
                f"El equipo de {self.nombre} ya tiene {CAPACIDAD_MAXIMA_EQUIPO} criaturas.",
                capacidad_maxima=CAPACIDAD_MAXIMA_EQUIPO,
            )
        self.equipo.append(criatura)

    def criatura_activa(self) -> Optional["Criatura"]:
        """
        Retorna la primera criatura del equipo que no esté debilitada.

        Retorna:
            Optional[Criatura]: La criatura activa, o None si todas están debilitadas.
        """
        for c in self.equipo:
            if not c.esta_debilitada():
                return c
        return None

    # ─────────────────────────────────────────
    # INVENTARIO
    # ─────────────────────────────────────────

    def agregar_item(self, item: "Item") -> None:
        """
        Agrega un ítem al inventario del jugador.

        Parámetros:
            item (Item): El ítem a agregar.

        Retorna:
            None
        """
        self.inventario.append(item)

    def tiene_item(self, nombre_item: str) -> bool:
        """
        Verifica si el jugador tiene un ítem con el nombre dado en el inventario.

        Parámetros:
            nombre_item (str): Nombre del ítem a buscar.

        Retorna:
            bool: True si el ítem está en el inventario.
        """
        return any(i.nombre == nombre_item for i in self.inventario)

    def obtener_item(self, nombre_item: str) -> "Item":
        """
        Busca y retorna un ítem del inventario por nombre.

        Parámetros:
            nombre_item (str): Nombre del ítem a buscar.

        Retorna:
            Item: El ítem encontrado.

        Lanza:
            ItemNoDisponibleError: Si el ítem no está en el inventario.
        """
        for item in self.inventario:
            if item.nombre == nombre_item:
                return item
        raise ItemNoDisponibleError(
            f"'{nombre_item}' no está en el inventario.",
            nombre_item=nombre_item,
        )

    def consumir_item(self, nombre_item: str) -> None:
        """
        Elimina un ítem del inventario (para ítems consumibles).

        Parámetros:
            nombre_item (str): Nombre del ítem a consumir.

        Retorna:
            None

        Lanza:
            ItemNoDisponibleError: Si el ítem no está en el inventario.
        """
        item = self.obtener_item(nombre_item)
        self.inventario.remove(item)

    # ─────────────────────────────────────────
    # EQUIPAR ÍTEM
    # ─────────────────────────────────────────

    def equipar_item(self, criatura: "Criatura", nombre_item: str) -> None:
        """
        Equipa un ítem a una criatura del equipo del jugador.

        Si la criatura ya tiene un ítem equipado, se revierte su efecto
        antes de aplicar el nuevo. El ítem debe estar en el inventario.

        Parámetros:
            criatura (Criatura): La criatura a la que se equipa el ítem.
            nombre_item (str): Nombre del ítem del inventario a equipar.

        Retorna:
            None

        Lanza:
            ItemNoDisponibleError: Si el ítem no está en el inventario.
            CriaturaDebilitadaError: Si la criatura está debilitada.
        """
        if criatura.esta_debilitada():
            raise CriaturaDebilitadaError(
                f"No se puede equipar un ítem a {criatura.nombre}: está debilitada.",
                nombre_criatura=criatura.nombre,
            )

        nuevo_item = self.obtener_item(nombre_item)

        # Revertir ítem anterior si existe
        if criatura.item_equipado is not None:
            criatura.item_equipado.modificar_estadistica(criatura, revertir=True)

        # Aplicar nuevo ítem
        nuevo_item.modificar_estadistica(criatura, revertir=False)
        criatura.item_equipado = nuevo_item

    # ─────────────────────────────────────────
    # CAPTURA
    # ─────────────────────────────────────────

    def capturar_criatura(self, criatura: "Criatura", nombre_item_captura: str) -> None:
        """
        Intenta capturar una criatura salvaje usando un ítem de captura.

        La probabilidad de éxito aumenta a menor HP de la criatura.
        Si la captura es exitosa, la criatura se añade al equipo y el
        ítem se consume del inventario.

        Parámetros:
            criatura (Criatura): La criatura salvaje a capturar.
            nombre_item_captura (str): Nombre del ítem de captura a usar.

        Retorna:
            None

        Lanza:
            ItemNoDisponibleError: Si el ítem no está en el inventario.
            EquipoLlenoError: Si el equipo ya tiene 6 criaturas.
            CapturaFallidaError: Si la captura falla por probabilidad.
        """
        import random
        from excepciones import CapturaFallidaError

        item = self.obtener_item(nombre_item_captura)

        if not item.es_captura:
            raise ItemNoDisponibleError(
                f"'{nombre_item_captura}' no es un ítem de captura.",
                nombre_item=nombre_item_captura,
            )

        # Probabilidad basada en HP restante: cuanto menos HP, más fácil capturar
        ratio_hp = criatura.hp / criatura.hp_max
        probabilidad = max(0.10, 1.0 - ratio_hp * 0.85)

        self.consumir_item(nombre_item_captura)

        if random.random() > probabilidad:
            raise CapturaFallidaError(
                f"{criatura.nombre} escapó del intento de captura.",
                nombre_criatura=criatura.nombre,
            )

        self.agregar_criatura(criatura)

    # ─────────────────────────────────────────
    # PERSISTENCIA
    # ─────────────────────────────────────────

    def guardar(self, ruta: str = "partida.json") -> None:
        """
        Serializa el estado del jugador en un archivo JSON.

        Parámetros:
            ruta (str): Ruta del archivo de guardado. Por defecto 'partida.json'.

        Retorna:
            None

        Lanza:
            OSError: Si no se puede escribir el archivo.
        """
        datos = {
            "nombre": self.nombre,
            "posicion": self.posicion,
            "equipo": [
                {
                    "nombre": c.nombre,
                    "tipo": c.tipo.nombre,
                    "hp": c.hp,
                    "hp_max": c.hp_max,
                    "atk": c.atk,
                    "defensa": c.defensa,
                    "velocidad": c.velocidad,
                    "precision": c.precision,
                    "nivel": c.nivel,
                    "experiencia": c.experiencia,
                    "xp_siguiente": c.xp_siguiente,
                }
                for c in self.equipo
            ],
            "inventario": [
                {
                    "nombre": i.nombre,
                    "descripcion": i.descripcion,
                    "efecto_positivo": i.efecto_positivo,
                    "efecto_negativo": i.efecto_negativo,
                    "es_consumible": i.es_consumible,
                    "es_captura": i.es_captura,
                }
                for i in self.inventario
            ],
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    @classmethod
    def cargar(cls, ruta: str = "partida.json") -> "Jugador":
        """
        Carga y reconstruye un Jugador desde un archivo JSON.

        Parámetros:
            ruta (str): Ruta del archivo de guardado.

        Retorna:
            Jugador: La instancia restaurada con su equipo e inventario.

        Lanza:
            PartidaNoEncontradaError: Si el archivo no existe.
            json.JSONDecodeError: Si el archivo está corrupto.
        """
        from excepciones import PartidaNoEncontradaError
        from criatura import Criatura
        from item import Item

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except FileNotFoundError:
            raise PartidaNoEncontradaError(
                f"No se encontró la partida guardada en '{ruta}'.",
                ruta=ruta,
            )

        jugador = cls(datos["nombre"], datos["posicion"])

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
            )
            c.hp = cd["hp"]
            c.experiencia = cd["experiencia"]
            c.xp_siguiente = cd["xp_siguiente"]
            jugador.equipo.append(c)

        for id_ in datos["inventario"]:
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

    # ─────────────────────────────────────────
    # REPRESENTACIÓN
    # ─────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Jugador(nombre='{self.nombre}', posicion='{self.posicion}', "
            f"criaturas={len(self.equipo)}, items={len(self.inventario)})"
        )

    def __str__(self) -> str:
        return (
            f"Jugador: {self.nombre} | Zona: {self.posicion} | "
            f"Criaturas: {len(self.equipo)}/{CAPACIDAD_MAXIMA_EQUIPO} | "
            f"Ítems: {len(self.inventario)}"
        )
