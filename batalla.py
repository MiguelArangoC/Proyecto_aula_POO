"""
batalla.py
==========
Define la clase Batalla, que gestiona el flujo de combate por turnos
entre la criatura activa del jugador y una criatura enemiga.

Cambios en esta versión
-----------------------
  - ejecutar_turno() acepta nombre_habilidad para usar habilidades reales
    a través de Habilidad.usar(). Si el nombre no existe o la criatura
    no tiene MP, hace fallback a Atacar.
  - La criatura del jugador recupera MP_RECUPERACION_TURNO cada turno.
  - El enemigo sigue usando el ataque base (IA simple).
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
    EN_CURSO  = auto()
    VICTORIA  = auto()
    DERROTA   = auto()
    RETIRADA  = auto()


class Batalla:
    """
    Gestiona el combate por turnos entre la criatura del jugador y un enemigo.
    """

    XP_POR_VICTORIA: int = 50

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
                jugador.equipo[0].nombre,
            )

        if enemigo.esta_debilitada():
            raise CriaturaDebilitadaError(
                "No se puede iniciar una batalla contra un enemigo debilitado.",
                enemigo.nombre,
            )

        self.jugador: "Jugador"             = jugador
        self.enemigo: "Criatura"            = enemigo
        self.condicion_climatica: CondicionClimatica = CondicionClimatica(nombre_clima)
        self.turno: int                     = 1
        self.estado: EstadoBatalla          = EstadoBatalla.EN_CURSO
        self.log: list[str]                 = []

        self._registrar(
            f"¡Ha comenzado la batalla contra {enemigo.nombre}! "
            f"[{self.condicion_climatica.nombre}]"
        )

    # ─────────────────────────────────────────
    # UTILIDADES INTERNAS
    # ─────────────────────────────────────────

    def _registrar(self, mensaje: str) -> None:
        self.log.append(f"[Turno {self.turno}] {mensaje}")

    def _ejecutar_ataque_base(
        self, atacante: "Criatura", defensor: "Criatura"
    ) -> tuple[bool, int, float]:
        """Ataque físico genérico (usado por el enemigo)."""
        if random.random() > atacante.precision:
            return False, 0, 1.0

        mod_clima = self.condicion_climatica.modificador_ataque(atacante.tipo.nombre)
        dano_base = random.randint(int(atacante.atk * 0.8), int(atacante.atk * 1.2))
        mult_tipo = atacante.tipo.calcular_multiplicador(defensor.tipo)
        dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - defensor.defensa // 2)
        defensor.hp = max(0, defensor.hp - dano_final)
        return True, dano_final, mult_tipo

    # ─────────────────────────────────────────
    # EJECUCIÓN DE TURNO
    # ─────────────────────────────────────────

    def ejecutar_turno(
        self,
        usar_item: bool = False,
        nombre_item: str = "",
        nombre_habilidad: str = "",
    ) -> EstadoBatalla:
        """
        Ejecuta un turno completo:
          1. Recuperación de MP para la criatura del jugador.
          2. Daño climático a ambas criaturas.
          3. Uso de ítem si se solicita.
          4. La criatura del jugador usa la habilidad indicada (o 'Atacar').
          5. El enemigo usa su ataque base.
          El orden de ataque depende de la velocidad.

        Parámetros:
            usar_item (bool):       Si True, equipa nombre_item antes de atacar.
            nombre_item (str):      Ítem a equipar.
            nombre_habilidad (str): Nombre de la habilidad del jugador este turno.

        Retorna:
            EstadoBatalla actual.
        """
        if self.estado != EstadoBatalla.EN_CURSO:
            raise RuntimeError("La batalla ya ha terminado.")

        criatura_jugador = self.jugador.criatura_activa()
        if criatura_jugador is None:
            self.estado = EstadoBatalla.DERROTA
            self._registrar("El jugador no tiene criaturas disponibles. ¡Derrota!")
            return self.estado

        # 1. Recuperar MP
        criatura_jugador.recuperar_mp_turno()

        # 2. Daño climático
        dano_j = self.condicion_climatica.aplicar_dano_turno(criatura_jugador)
        dano_e = self.condicion_climatica.aplicar_dano_turno(self.enemigo)
        if dano_j:
            self._registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_j} de daño a {criatura_jugador.nombre}."
            )
        if dano_e:
            self._registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_e} de daño a {self.enemigo.nombre}."
            )

        if self._verificar_fin():
            self.turno += 1
            return self.estado

        # 3. Usar ítem
        if usar_item:
            if not nombre_item:
                from excepciones import ItemNoDisponibleError
                raise ItemNoDisponibleError("Nombre de ítem no proporcionado.", "")
            self.jugador.equipar_item(criatura_jugador, nombre_item)
            self._registrar(
                f"{self.jugador.nombre} usa {nombre_item} en {criatura_jugador.nombre}."
            )

        # 4. Resolver orden por velocidad
        jugador_primero = criatura_jugador.velocidad >= self.enemigo.velocidad

        if jugador_primero:
            self._turno_jugador(criatura_jugador, nombre_habilidad)
            if not self._verificar_fin():
                self._turno_enemigo(criatura_jugador)
        else:
            self._turno_enemigo(criatura_jugador)
            if not self._verificar_fin():
                self._turno_jugador(criatura_jugador, nombre_habilidad)

        self._verificar_fin()
        # Limpiar estado temporal de esquiva
        criatura_jugador.limpiar_estado_turno()
        self.turno += 1
        return self.estado

    def _turno_jugador(self, criatura: "Criatura", nombre_habilidad: str) -> None:
        """Ejecuta la acción del jugador usando la habilidad seleccionada."""
        if criatura.esta_debilitada():
            return

        habilidad = criatura.obtener_habilidad(nombre_habilidad) if nombre_habilidad else None

        # Fallback a 'Atacar' si no se encontró o no tiene MP
        if habilidad is None or not habilidad.puede_usarse(criatura):
            if habilidad and not habilidad.puede_usarse(criatura):
                self._registrar(
                    f"{criatura.nombre} no tiene MP para {habilidad.nombre} "
                    f"(necesita {habilidad.costo_mp} MP, tiene {criatura.mp} MP). "
                    f"Usa Atacar en su lugar."
                )
            habilidad = criatura.obtener_habilidad("Atacar")

        if habilidad is None:
            return

        if habilidad.nombre == "Atacar":
            if random.random() > criatura.precision:
                self._registrar(f"{criatura.nombre} falló su ataque.")
            else:
                dano_base = random.randint(int(criatura.atk * 0.8), int(criatura.atk * 1.2))
                mult_tipo = criatura.tipo.calcular_multiplicador(self.enemigo.tipo)
                dano = max(1, int(dano_base * mult_tipo) - self.enemigo.defensa // 2)
                self.enemigo.hp = max(0, self.enemigo.hp - dano)
                self._registrar(
                    f"{criatura.nombre} usa Atacar contra {self.enemigo.nombre} -> "
                    f"{dano} de daño (tipo x{mult_tipo:.2f})."
                )
            return

        mod_clima = self.condicion_climatica.modificador_ataque(criatura.tipo.nombre)
        resultado = habilidad.usar(criatura, self.enemigo, mod_clima)
        self._registrar(resultado["mensaje"])

    def _turno_enemigo(self, criatura_jugador: "Criatura") -> None:
        """El enemigo siempre usa ataque base (IA simple)."""
        if self.enemigo.esta_debilitada() or criatura_jugador.esta_debilitada():
            return

        # Modificar precisión si el jugador activó esquiva
        precision_original = self.enemigo.precision
        if criatura_jugador._evasivo:
            self.enemigo.precision = self.enemigo.precision * 0.50

        conecto, dano, mult_tipo = self._ejecutar_ataque_base(self.enemigo, criatura_jugador)

        # Restaurar precisión
        self.enemigo.precision = precision_original

        if conecto:
            self._registrar(
                f"{self.enemigo.nombre} ataca a {criatura_jugador.nombre} -> "
                f"{dano} de daño (tipo x{mult_tipo:.2f})."
            )
        else:
            self._registrar(f"{self.enemigo.nombre} falló su ataque.")

    def retirarse(self) -> EstadoBatalla:
        """Marca la batalla como retirada y registra el evento."""
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

    def resumen(self) -> str:
        """Retorna un resumen textual del estado actual del combate."""
        criatura_jugador = self.jugador.criatura_activa()
        nombre_j, hp_j, mp_j = (
            (criatura_jugador.nombre, criatura_jugador.hp, criatura_jugador.mp)
            if criatura_jugador else ("Ninguna", 0, 0)
        )
        return (
            f"Estado: {self.estado.name}\n"
            f"Turno: {self.turno}\n"
            f"Jugador: {nombre_j} HP={hp_j} MP={mp_j}\n"
            f"Enemigo: {self.enemigo.nombre} HP={self.enemigo.hp}\n"
            f"Clima: {self.condicion_climatica.nombre}"
        )
