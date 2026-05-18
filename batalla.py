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

    def _registrar(self, mensaje: str) -> None:
        self.log.append(f"[Turno {self.turno}] {mensaje}")

    def _ejecutar_ataque(self, atacante: "Criatura", defensor: "Criatura") -> tuple[bool, int, float]:
        """Ejecuta un ataque invocando el multiplicador de tipos en Batalla."""
        if random.random() > atacante.precision:
            return False, 0, 1.0

        dano_base = random.randint(int(atacante.atk * 0.8), int(atacante.atk * 1.2))
        mult_tipo = atacante.tipo.calcular_multiplicador(defensor.tipo)
        dano_final = max(1, int(dano_base * mult_tipo) - defensor.defensa // 2)
        defensor.hp = max(0, defensor.hp - dano_final)
        return True, dano_final, mult_tipo

    def ejecutar_turno(self, usar_item: bool = False, nombre_item: str = "") -> EstadoBatalla:
        """
        Ejecuta un turno de combate completo: aplica daño climático, gestiona
        el uso de ítem si se solicita, y resuelve los ataques por velocidad.

        Parámetros:
            usar_item (bool): Si True, equipa el ítem indicado antes de atacar.
            nombre_item (str): Nombre del ítem a equipar (requerido si usar_item=True).

        Retorna:
            EstadoBatalla: El estado resultante tras el turno.

        Lanza:
            RuntimeError: Si la batalla ya terminó.
            ItemNoDisponibleError: Si usar_item=True pero nombre_item está vacío.
        """
        if self.estado != EstadoBatalla.EN_CURSO:
            raise RuntimeError("La batalla ya ha terminado.")

        criatura_jugador = self.jugador.criatura_activa()
        if criatura_jugador is None:
            self.estado = EstadoBatalla.DERROTA
            self._registrar("El jugador no tiene criaturas disponibles. ¡Derrota!")
            return self.estado

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

        if self._verificar_fin():
            self.turno += 1
            return self.estado

        if usar_item:
            if not nombre_item:
                from excepciones import ItemNoDisponibleError
                raise ItemNoDisponibleError("Nombre de ítem no proporcionado.", "")
            self.jugador.equipar_item(criatura_jugador, nombre_item)
            self._registrar(f"{self.jugador.nombre} usa {nombre_item} en {criatura_jugador.nombre}.")

        jugador_primero = criatura_jugador.velocidad >= self.enemigo.velocidad

        atacantes = (
            [(criatura_jugador, self.enemigo), (self.enemigo, criatura_jugador)]
            if jugador_primero
            else [(self.enemigo, criatura_jugador), (criatura_jugador, self.enemigo)]
        )

        for atacante, defensor in atacantes:
            if atacante.esta_debilitada() or defensor.esta_debilitada():
                continue

            mod_clima = self.condicion_climatica.modificador_ataque(atacante.tipo.nombre)
            atk_original = atacante.atk
            atacante.atk = int(atacante.atk * mod_clima)

            conecto, dano, mult_tipo = self._ejecutar_ataque(atacante, defensor)
            atacante.atk = atk_original

            if conecto:
                self._registrar(
                    f"{atacante.nombre} ataca a {defensor.nombre} -> {dano} de dano "
                    f"(tipo x{mult_tipo:.2f}, clima x{mod_clima:.2f})."
                )
            else:
                self._registrar(f"{atacante.nombre} falló su ataque.")

            if self._verificar_fin():
                break

        self.turno += 1
        return self.estado

    def retirarse(self) -> EstadoBatalla:
        """
        El jugador abandona voluntariamente la batalla.

        Retorna:
            EstadoBatalla: RETIRADA.
        """
        self.estado = EstadoBatalla.RETIRADA
        self._registrar(f"{self.jugador.nombre} se retiró de la batalla.")
        return self.estado

    def _verificar_fin(self) -> bool:
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
        Genera un texto con el estado actual de la batalla.

        Retorna:
            str: Resumen legible del estado, turno, HP de ambas criaturas y clima.
        """
        criatura_jugador = self.jugador.criatura_activa()
        nombre_j, hp_j = (criatura_jugador.nombre, criatura_jugador.hp) if criatura_jugador else ("Ninguna", 0)

        return (
            f"Estado: {self.estado.name}\n"
            f"Turno: {self.turno}\n"
            f"Jugador: {nombre_j} HP={hp_j}\n"
            f"Enemigo: {self.enemigo.nombre} HP={self.enemigo.hp}\n"
            f"Clima: {self.condicion_climatica.nombre}"
        )
