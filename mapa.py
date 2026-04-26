"""
mapa.py
=======
Define las clases Zona y Mapa, que representan la estructura
de navegación del mundo del juego.

- Zona: representa un área geográfica con criaturas y clima propios.
- Mapa: gestiona las zonas y las conexiones de navegación entre ellas.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from excepciones import ZonaInexistenteError

if TYPE_CHECKING:
    from condicion_climatica import CondicionClimatica


class Zona:
    """
    Representa una zona geográfica del mapa del juego.

    Cada zona tiene un clima base, una lista de criaturas salvajes que
    pueden aparecer y conexiones hacia otras zonas (norte, sur, este, oeste).

    Atributos:
        nombre (str): Nombre identificador de la zona.
        clima_base (str): Nombre del clima predominante (ej. 'Soleado').
        criaturas_salvajes (list[str]): Nombres de criaturas que pueden aparecer.
        conexiones (dict[str, str]): Mapa de dirección → nombre de zona conectada.
    """

    def __init__(
        self,
        nombre: str,
        clima_base: str,
        criaturas_salvajes: list[str],
        conexiones: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Inicializa una zona del juego.

        Parámetros:
            nombre (str): Nombre de la zona (no puede estar vacío).
            clima_base (str): Nombre del clima base de la zona.
            criaturas_salvajes (list[str]): Nombres de criaturas posibles en la zona.
            conexiones (dict[str, str] | None): Diccionario {dirección: nombre_zona}.
                Si es None, se inicializa como dict vacío.

        Lanza:
            ValueError: Si el nombre de la zona está vacío.
        """
        if not nombre.strip():
            raise ValueError("El nombre de la zona no puede estar vacío.")

        self.nombre: str = nombre
        self.clima_base: str = clima_base
        self.criaturas_salvajes: list[str] = criaturas_salvajes
        self.conexiones: dict[str, str] = conexiones if conexiones is not None else {}

    def agregar_conexion(self, direccion: str, nombre_zona: str) -> None:
        """
        Agrega o actualiza una conexión desde esta zona hacia otra.

        Parámetros:
            direccion (str): Dirección de la conexión ('norte', 'sur', 'este', 'oeste').
            nombre_zona (str): Nombre de la zona destino.

        Retorna:
            None
        """
        self.conexiones[direccion] = nombre_zona

    def obtener_criatura_aleatoria(self) -> Optional[str]:
        """
        Retorna el nombre de una criatura salvaje aleatoria de la zona.

        Retorna:
            Optional[str]: Nombre de la criatura o None si la lista está vacía.
        """
        import random
        if not self.criaturas_salvajes:
            return None
        return random.choice(self.criaturas_salvajes)

    def __repr__(self) -> str:
        return (
            f"Zona(nombre='{self.nombre}', clima='{self.clima_base}', "
            f"conexiones={list(self.conexiones.keys())})"
        )

    def __str__(self) -> str:
        dirs_ = ", ".join(
            f"{d} -> {z}" for d, z in self.conexiones.items()
        )
        return f"{self.nombre} [{self.clima_base}] | Salidas: {dirs_ or 'ninguna'}"


class Mapa:
    """
    Gestiona la colección de zonas y las conexiones de navegación.

    Atributos:
        zonas (dict[str, Zona]): Diccionario de zonas registradas por nombre.
    """

    def __init__(self) -> None:
        """
        Inicializa un mapa vacío.
        """
        self.zonas: dict[str, Zona] = {}

    def agregar_zona(self, zona: Zona) -> None:
        """
        Registra una zona en el mapa.

        Parámetros:
            zona (Zona): La zona a agregar.

        Retorna:
            None
        """
        self.zonas[zona.nombre] = zona

    def obtener_zona(self, nombre: str) -> Zona:
        """
        Busca y retorna una zona por su nombre.

        Parámetros:
            nombre (str): Nombre de la zona a buscar.

        Retorna:
            Zona: La zona encontrada.

        Lanza:
            ZonaInexistenteError: Si no existe una zona con ese nombre.
        """
        if nombre not in self.zonas:
            raise ZonaInexistenteError(
                f"La zona '{nombre}' no existe en el mapa.",
                nombre,
            )
        return self.zonas[nombre]

    def zonas_adyacentes(self, nombre: str) -> dict[str, str]:
        """
        Retorna las zonas accesibles desde una zona dada.

        Parámetros:
            nombre (str): Nombre de la zona origen.

        Retorna:
            dict[str, str]: Diccionario {dirección: nombre_zona_destino}.

        Lanza:
            ZonaInexistenteError: Si la zona origen no existe en el mapa.
        """
        return self.obtener_zona(nombre).conexiones

    @classmethod
    def crear_mapa_default(cls) -> "Mapa":
        """
        Crea y retorna el mapa por defecto del juego con todas sus zonas.

        Retorna:
            Mapa: Instancia del mapa con zonas y conexiones configuradas.
        """
        mapa = cls()

        zonas_data = [
            Zona(
                nombre="Pradera",
                clima_base="Soleado",
                criaturas_salvajes=["Ignis", "Torrente"],
                conexiones={"norte": "Volcán", "este": "Lago"},
            ),
            Zona(
                nombre="Volcán",
                clima_base="Caluroso",
                criaturas_salvajes=["Ignis", "Rocafer"],
                conexiones={"sur": "Pradera"},
            ),
            Zona(
                nombre="Lago",
                clima_base="Lluvioso",
                criaturas_salvajes=["Torrente", "Voltex"],
                conexiones={"oeste": "Pradera"},
            ),
        ]

        for zona in zonas_data:
            mapa.agregar_zona(zona)

        return mapa

    def __repr__(self) -> str:
        return f"Mapa(zonas={list(self.zonas.keys())})"

    def __str__(self) -> str:
        lineas = [f"=== MAPA DEL MUNDO ==="]
        for nombre, zona in self.zonas.items():
            lineas.append(f"  {zona}")
        return "\n".join(lineas)
