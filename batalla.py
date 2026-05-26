"""
batalla.py
==========
Define la clase Batalla, que gestiona el flujo de combate por turnos
entre la criatura activa del jugador y una criatura enemiga.
"""

import random
from enum import Enum, auto

from condicion_climatica import CondicionClimatica
from excepciones import CriaturaDebilitadaError


class EstadoBatalla(Enum):
    EN_CURSO  = auto()
    VICTORIA  = auto()
    DERROTA   = auto()
    RETIRADA  = auto()


class Batalla:
    """
    Gestiona el combate por turnos entre la criatura del jugador y un enemigo.
    """

    XP_POR_VICTORIA = 50

    def __init__(self, jugador, enemigo, nombre_clima="Soleado"):
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

        self.jugador             = jugador
        self.enemigo             = enemigo
        self.condicion_climatica = CondicionClimatica(nombre_clima)
        self.turno               = 1
        self.estado              = EstadoBatalla.EN_CURSO
        self.log                 = []

        self.registrar(
            f"¡Ha comenzado la batalla contra {enemigo.nombre}! "
            f"[{self.condicion_climatica.nombre}]"
        )

    # ─────────────────────────────────────────
    # UTILIDADES INTERNAS
    # ─────────────────────────────────────────

    def registrar(self, mensaje):
        self.log.append(f"[Turno {self.turno}] {mensaje}")

    def ejecutar_ataque_base(self, atacante, defensor):
        """Ataque físico genérico usado por el enemigo. Retorna (conecto, dano, mult_tipo)."""
        if random.random() > atacante.precision:
            return False, 0, 1.0

        mod_clima  = self.condicion_climatica.modificador_ataque(atacante.tipo.nombre)
        dano_base  = random.randint(int(atacante.atk * 0.8), int(atacante.atk * 1.2))
        mult_tipo  = atacante.tipo.calcular_multiplicador(defensor.tipo)
        dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - defensor.defensa // 2)
        defensor.hp = max(0, defensor.hp - dano_final)
        return True, dano_final, mult_tipo

    # ─────────────────────────────────────────
    # EJECUCIÓN DE TURNO
    # ─────────────────────────────────────────

    def ejecutar_turno(self, usar_item=False, nombre_item="", nombre_habilidad=""):
        """
        Ejecuta un turno completo:
          1. La criatura del jugador recupera MP.
          2. El clima aplica daño a ambas criaturas.
          3. Si usar_item=True, equipa el ítem indicado.
          4. La criatura del jugador usa la habilidad indicada (o 'Atacar').
          5. El enemigo usa su ataque base.
          El orden de ataque depende de la velocidad.
        Retorna el estado actual de la batalla.
        """
        if self.estado != EstadoBatalla.EN_CURSO:
            raise ValueError("La batalla ya ha terminado.")

        criatura_jugador = self.jugador.criatura_activa()
        if criatura_jugador is None:
            self.estado = EstadoBatalla.DERROTA
            self.registrar("El jugador no tiene criaturas disponibles. ¡Derrota!")
            return self.estado

        # 1. Recuperar MP
        criatura_jugador.recuperar_mp_turno()

        # 2. Daño climático
        dano_j = self.condicion_climatica.aplicar_dano_turno(criatura_jugador)
        dano_e = self.condicion_climatica.aplicar_dano_turno(self.enemigo)
        if dano_j:
            self.registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_j} de daño a {criatura_jugador.nombre}."
            )
        if dano_e:
            self.registrar(
                f"El clima {self.condicion_climatica.nombre} hace "
                f"{dano_e} de daño a {self.enemigo.nombre}."
            )

        if self.verificar_fin():
            self.turno += 1
            return self.estado

        # 3. Usar ítem
        if usar_item:
            if not nombre_item:
                from excepciones import ItemNoDisponibleError
                raise ItemNoDisponibleError("Nombre de ítem no proporcionado.", "")
            self.jugador.equipar_item(criatura_jugador, nombre_item)
            self.registrar(
                f"{self.jugador.nombre} usa {nombre_item} en {criatura_jugador.nombre}."
            )

        # 4. Resolver orden por velocidad
        jugador_primero = criatura_jugador.velocidad >= self.enemigo.velocidad

        if jugador_primero:
            self.turno_jugador(criatura_jugador, nombre_habilidad)
            if not self.verificar_fin():
                self.turno_enemigo(criatura_jugador)
        else:
            self.turno_enemigo(criatura_jugador)
            if not self.verificar_fin():
                self.turno_jugador(criatura_jugador, nombre_habilidad)

        self.verificar_fin()
        criatura_jugador.limpiar_estado_turno()
        self.turno += 1
        return self.estado

    def turno_jugador(self, criatura, nombre_habilidad):
        """Ejecuta la acción del jugador con la habilidad seleccionada."""
        if criatura.esta_debilitada():
            return

        habilidad = None
        if nombre_habilidad:
            habilidad = criatura.obtener_habilidad(nombre_habilidad)

        # Si no se encontró la habilidad o no hay MP suficiente, usar Atacar
        if habilidad is None or not habilidad.puede_usarse(criatura):
            if habilidad is not None and not habilidad.puede_usarse(criatura):
                self.registrar(
                    f"{criatura.nombre} no tiene MP para {habilidad.nombre} "
                    f"(necesita {habilidad.costo_mp} MP, tiene {criatura.mp} MP). "
                    f"Usa Atacar en su lugar."
                )
            habilidad = criatura.obtener_habilidad("Atacar")

        if habilidad is None:
            return

        if habilidad.nombre == "Atacar":
            if random.random() > criatura.precision:
                self.registrar(f"{criatura.nombre} falló su ataque.")
            else:
                dano_base = random.randint(int(criatura.atk * 0.8), int(criatura.atk * 1.2))
                mult_tipo = criatura.tipo.calcular_multiplicador(self.enemigo.tipo)
                dano      = max(1, int(dano_base * mult_tipo) - self.enemigo.defensa // 2)
                self.enemigo.hp = max(0, self.enemigo.hp - dano)
                self.registrar(
                    f"{criatura.nombre} usa Atacar contra {self.enemigo.nombre} -> "
                    f"{dano} de daño (tipo x{mult_tipo:.2f})."
                )
            return

        mod_clima  = self.condicion_climatica.modificador_ataque(criatura.tipo.nombre)
        resultado  = habilidad.usar(criatura, self.enemigo, mod_clima)
        self.registrar(resultado["mensaje"])

    def turno_enemigo(self, criatura_jugador):
        """El enemigo siempre usa ataque base (IA simple)."""
        if self.enemigo.esta_debilitada() or criatura_jugador.esta_debilitada():
            return

        # Si el jugador activó esquiva, reducir la precisión del enemigo este turno
        precision_original = self.enemigo.precision
        if criatura_jugador.evasivo:
            self.enemigo.precision = self.enemigo.precision * 0.50

        conecto, dano, mult_tipo = self.ejecutar_ataque_base(self.enemigo, criatura_jugador)

        # Restaurar precisión original
        self.enemigo.precision = precision_original

        if conecto:
            self.registrar(
                f"{self.enemigo.nombre} ataca a {criatura_jugador.nombre} -> "
                f"{dano} de daño (tipo x{mult_tipo:.2f})."
            )
        else:
            self.registrar(f"{self.enemigo.nombre} falló su ataque.")

    def retirarse(self):
        """Marca la batalla como retirada."""
        self.estado = EstadoBatalla.RETIRADA
        self.registrar(f"{self.jugador.nombre} se retiró de la batalla.")
        return self.estado

    def verificar_fin(self):
        """Verifica si la batalla terminó y actualiza el estado."""
        if self.enemigo.esta_debilitada():
            self.estado   = EstadoBatalla.VICTORIA
            xp_ganada     = self.XP_POR_VICTORIA + self.enemigo.nivel * 10
            criatura      = self.jugador.criatura_activa()
            if criatura:
                subio = criatura.ganar_experiencia(xp_ganada)
                self.registrar(
                    f"¡Victoria! {criatura.nombre} ganó {xp_ganada} XP."
                    + (f" ¡{criatura.nombre} subió al nivel {criatura.nivel}!" if subio else "")
                )
            return True

        if self.jugador.criatura_activa() is None:
            self.estado = EstadoBatalla.DERROTA
            self.registrar("¡Todas las criaturas del jugador están debilitadas! Derrota.")
            return True

        return False

    def resumen(self):
        """Retorna un resumen textual del estado actual del combate."""
        criatura_jugador = self.jugador.criatura_activa()
        if criatura_jugador:
            nombre_j = criatura_jugador.nombre
            hp_j     = criatura_jugador.hp
            mp_j     = criatura_jugador.mp
        else:
            nombre_j = "Ninguna"
            hp_j     = 0
            mp_j     = 0

        return (
            f"Estado: {self.estado.name}\n"
            f"Turno: {self.turno}\n"
            f"Jugador: {nombre_j} HP={hp_j} MP={mp_j}\n"
            f"Enemigo: {self.enemigo.nombre} HP={self.enemigo.hp}\n"
            f"Clima: {self.condicion_climatica.nombre}"
        )
