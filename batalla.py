"""
batalla.py
==========
Define la clase Batalla, que gestiona el flujo de combate por turnos
entre la criatura activa del jugador y una criatura enemiga.

Maneja el turno, el estado de la batalla y la condición climática activa.
"""

from __future__ import annotations
import random
from enum import Enum, auto
from typing import TYPE_CHECKING

from condicion_climatica import CondicionClimatica

if TYPE_CHECKING:
    from criatura import Criatura
    from jugador import Jugador


class EstadoBatalla(Enum):
    """
    Enumeración de los posibles estados de una batalla.

    Valores:
        EN_CURSO: La batalla está activa y sigue en progreso.
        VICTORIA: El jugador ganó la batalla.
        DERROTA: El jugador perdió (todas sus criaturas están debilitadas).
        RETIRADA: El jugador decidió retirarse voluntariamente.
    """
    EN_CURSO = auto()
    VICTORIA = auto()
    DERROTA = auto()
    RETIRADA = auto()


class Batalla:
    """
    Gestiona el combate por turnos entre la criatura del jugador y un enemigo.

    Atributos:
        jugador (Jugador): El jugador que participa en la batalla.
        enemigo (Criatura): La criatura enemiga (salvaje o rival).
        condicion_climatica (CondicionClimatica): Clima activo durante el combate.
        turno (int): Número de turno actual (inicia en 1).
        estado (EstadoBatalla): Estado actual de la batalla.
        log (list[str]): Registro de eventos del combate en orden cronológico.
    """

    XP_POR_VICTORIA: int = 50   # Experiencia base otorgada al ganar

    def __init__(
        self,
        jugador: "Jugador",
        enemigo: "Criatura",
        nombre_clima: str = "Soleado",
    ) -> None:
        """
        Inicializa una batalla entre el jugador y una criatura enemiga.

        Parámetros:
            jugador (Jugador): El jugador participante.
            enemigo (Criatura): La criatura enemiga a enfrentar.
            nombre_clima (str): Nombre del clima activo. Por defecto 'Soleado'.

        Lanza:
            ValueError: Si el jugador no tiene ninguna criatura en su equipo.
            CriaturaDebilitadaError: Si la criatura enemiga o todas las del jugador están debilitadas.
        """
        from excepciones import CriaturaDebilitadaError

        if not jugador.equipo:
            raise ValueError("El jugador debe tener al menos una criatura para batallar.")

        if jugador.criatura_activa() is None:
            raise CriaturaDebilitadaError(
                "Todas las criaturas del jugador están debilitadas.",
                jugador.equipo[0].nombre
            )

        if enemigo.esta_debilitada():
            raise CriaturaDebilitadaError(
                "No se puede iniciar una batalla contra un enemigo debilitado.",
                enemigo.nombre
            )

        self.jugador: "Jugador" = jugador
        self.enemigo: "Criatura" = enemigo
        self.condicion_climatica: CondicionClimatica = CondicionClimatica(nombre_clima)
        self.turno: int = 1
        self.estado: EstadoBatalla = EstadoBatalla.EN_CURSO
        self.log: list[str] = []

        self._registrar(
            f"¡Ha comenzado la batalla contra {enemigo.nombre}! "
            f"[{self.condicion_climatica.nombre}]"
        )

    # ─────────────────────────────────────────
    # ACCESO INTERNO
    # ─────────────────────────────────────────

    def _registrar(self, mensaje: str) -> None:
        """
        Agrega un mensaje al log de la batalla.

        Parámetros:
            mensaje (str): Texto del evento a registrar.

        Retorna:
            None
        """
        self.log.append(f"[Turno {self.turno}] {mensaje}")

    # ─────────────────────────────────────────
    # EJECUCIÓN DE TURNO
    # ─────────────────────────────────────────

    def ejecutar_turno(self, usar_item: bool = False, nombre_item: str = "") -> EstadoBatalla:
        """
        Ejecuta un turno completo de combate.

        Orden de acciones por turno:
          1. Aplicar daño por turno del clima (a ambas criaturas).
          2. Opcionalmente usar un ítem sobre la criatura del jugador.
          3. Determinar el orden de ataque según velocidad.
          4. Atacar y aplicar daño con multiplicadores de tipo y clima.
          5. Verificar condición de fin de batalla.

        Parámetros:
            usar_item (bool): Si True, el jugador usa un ítem este turno.
            nombre_item (str): Nombre del ítem a usar (requerido si usar_item=True).

        Retorna:
            EstadoBatalla: El estado actualizado tras el turno.

        Lanza:
            RuntimeError: Si se llama cuando la batalla ya terminó.
            ItemNoDisponibleError: Si el ítem no existe en el inventario.
        """
        if self.estado != EstadoBatalla.EN_CURSO:
            raise RuntimeError("La batalla ya ha terminado.")

        criatura_jugador = self.jugador.criatura_activa()
        if criatura_jugador is None:
            self.estado = EstadoBatalla.DERROTA
            self._registrar("El jugador no tiene criaturas disponibles. ¡Derrota!")
            return self.estado

        # --- 1. Daño por turno del clima ---
        dano_clima_jugador = self.condicion_climatica.aplicar_dano_turno(criatura_jugador)
        dano_clima_enemigo = self.condicion_climatica.aplicar_dano_turno(self.enemigo)

        if dano_clima_jugador:
            self._registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_clima_jugador} de daño a {criatura_jugador.nombre}."
            )
        if dano_clima_enemigo:
            self._registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_clima_enemigo} de daño a {self.enemigo.nombre}."
            )

        # Verificar si alguno ya cayó por el clima
        if self._verificar_fin():
            self.turno += 1
            return self.estado

        # --- 2. Usar ítem (opcional) ---
        if usar_item:
            if not nombre_item:
                from excepciones import ItemNoDisponibleError
                raise ItemNoDisponibleError("Nombre de ítem no proporcionado.", "")
            self.jugador.equipar_item(criatura_jugador, nombre_item)
            self._registrar(f"{self.jugador.nombre} usa {nombre_item} en {criatura_jugador.nombre}.")


        # --- 3. Determinar orden de ataque por velocidad ---
        jugador_primero = criatura_jugador.velocidad >= self.enemigo.velocidad

        atacantes = (
            [(criatura_jugador, self.enemigo), (self.enemigo, criatura_jugador)]
            if jugador_primero
            else [(self.enemigo, criatura_jugador), (criatura_jugador, self.enemigo)]
        )

        # --- 4. Ejecutar ataques ---
        for atacante, defensor in atacantes:
            if atacante.esta_debilitada() or defensor.esta_debilitada():
                continue

            # Modificador de clima sobre el atacante
            mod_clima = self.condicion_climatica.modificador_ataque(atacante.tipo.nombre)
            atk_original = atacante.atk
            atacante.atk = int(atacante.atk * mod_clima)

            conectó, dano = atacante.atacar(defensor)

            atacante.atk = atk_original   # restaurar ataque original

            if conectó:
                self._registrar(
                    f"{atacante.nombre} ataca a {defensor.nombre} -> {dano} de dano "
                    f"(clima x{mod_clima:.2f})."
                )
            else:
                self._registrar(f"{atacante.nombre} falló su ataque.")

            if self._verificar_fin():
                break

        # --- 5. Avanzar turno ---
        self.turno += 1
        return self.estado

    def retirarse(self) -> EstadoBatalla:
        """
        El jugador decide retirarse de la batalla.

        Retorna:
            EstadoBatalla: RETIRADA siempre.
        """
        self.estado = EstadoBatalla.RETIRADA
        self._registrar(f"{self.jugador.nombre} se retiró de la batalla.")
        return self.estado

    # ─────────────────────────────────────────
    # VERIFICACIÓN DE FIN
    # ─────────────────────────────────────────

    def _verificar_fin(self) -> bool:
        """
        Comprueba si la batalla ha terminado y actualiza el estado.

        Retorna:
            bool: True si la batalla terminó (victoria o derrota).
        """
        if self.enemigo.esta_debilitada():
            self.estado = EstadoBatalla.VICTORIA
            xp_ganada = self.XP_POR_VICTORIA + self.enemigo.nivel * 10
            criatura = self.jugador.criatura_activa()
            if criatura:
                subio = criatura.ganar_experiencia(xp_ganada)
                self._registrar(
                    f"¡Victoria! {criatura.nombre} ganó {xp_ganada} XP."
                    + (f" ¡{criatura.nombre} subió al nivel {criatura.nivel}!" if subio else "")
                )
            return True

        if self.jugador.criatura_activa() is None:
            self.estado = EstadoBatalla.DERROTA
            self._registrar("¡Todas las criaturas del jugador están debilitadas! Derrota.")
            return True

        return False

    # ─────────────────────────────────────────
    # INFORMACIÓN
    # ─────────────────────────────────────────

    def resumen(self) -> str:
        """
        Retorna un resumen del estado actual de la batalla.

        Retorna:
            str: Texto con el turno, el clima y los HP de ambos participantes.
        """
        criatura = self.jugador.criatura_activa()
        jugador_str = (
            f"{criatura.nombre} HP:{criatura.hp}/{criatura.hp_max}"
            if criatura
            else "Sin criaturas"
        )
        return (
            f"--- Turno {self.turno} | {self.condicion_climatica.nombre} ---\n"
            f"  Jugador: {jugador_str}\n"
            f"  Enemigo: {self.enemigo.nombre} HP:{self.enemigo.hp}/{self.enemigo.hp_max}\n"
            f"  Estado: {self.estado.name}"
        )

    def __repr__(self) -> str:
        return (
            f"Batalla(enemigo='{self.enemigo.nombre}', turno={self.turno}, "
            f"estado={self.estado.name})"
        )
