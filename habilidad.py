"""
habilidad.py
============
Define la clase Habilidad, que representa una acción que una criatura
puede ejecutar en combate. Reemplaza el ataque genérico con acciones
diferenciadas: ataques normales, ataques especiales, esquiva y efectos
de estado.

Tipos de habilidad
------------------
  "ataque"    — inflige daño directo al enemigo.
  "especial"  — daño amplificado con ventaja de tipo (ignora parcialmente DEF).
  "esquivar"  — aumenta evasión del usuario durante el turno (reduce daño recibido).
  "soporte"   — restaura HP o MP del usuario.

Cada habilidad tiene un coste de MP. Si la criatura no tiene MP suficiente
la habilidad falla y se usa "Atacar" como fallback.
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from criatura import Criatura


class Habilidad:
    """
    Representa una habilidad usable en combate.

    Atributos:
        nombre (str): Nombre de la habilidad.
        tipo (str): Categoría funcional — 'ataque' | 'especial' | 'esquivar' | 'soporte'.
        costo_mp (int): MP consumido al usar la habilidad (0 para ataques básicos).
        potencia (float): Multiplicador de daño sobre el ATK base.
        precision_mod (float): Modificador sobre la precisión base del usuario.
        descripcion (str): Texto descriptivo para la GUI.
        icono (str): Emoji representativo para la GUI.
    """

    def __init__(
        self,
        nombre: str,
        tipo: str,
        costo_mp: int,
        potencia: float,
        precision_mod: float = 1.0,
        descripcion: str = "",
        icono: str = "✦",
    ) -> None:
        tipos_validos = {"ataque", "especial", "esquivar", "soporte"}
        if tipo not in tipos_validos:
            raise ValueError(f"Tipo de habilidad '{tipo}' no válido. Use: {tipos_validos}")
        if potencia < 0:
            raise ValueError("La potencia no puede ser negativa.")
        if costo_mp < 0:
            raise ValueError("El costo de MP no puede ser negativo.")

        self.nombre: str = nombre
        self.tipo: str = tipo
        self.costo_mp: int = costo_mp
        self.potencia: float = potencia
        self.precision_mod: float = precision_mod
        self.descripcion: str = descripcion
        self.icono: str = icono

    # ─────────────────────────────────────────
    # EJECUCIÓN EN COMBATE
    # ─────────────────────────────────────────

    def puede_usarse(self, usuario: "Criatura") -> bool:
        """Retorna True si el usuario tiene suficiente MP para usar esta habilidad."""
        return usuario.mp >= self.costo_mp

    def usar(
        self,
        usuario: "Criatura",
        objetivo: "Criatura",
        mod_clima: float = 1.0,
    ) -> dict:
        """
        Ejecuta la habilidad y retorna un reporte del resultado.

        Parámetros:
            usuario   (Criatura): Criatura que usa la habilidad.
            objetivo  (Criatura): Criatura objetivo (puede ser la misma para soporte).
            mod_clima (float):    Multiplicador de clima aplicado al ATK del usuario.

        Retorna:
            dict con claves:
                "conectó"   (bool)  — si la acción tuvo efecto.
                "daño"      (int)   — daño infligido (0 si no aplica).
                "curación"  (int)   — HP restaurado (0 si no aplica).
                "evasión"   (bool)  — si el usuario entró en estado evasivo.
                "mensaje"   (str)   — descripción del evento para el log.
        """
        resultado = {"conectó": False, "daño": 0, "curación": 0, "evasión": False, "mensaje": ""}

        # Verificar MP
        if not self.puede_usarse(usuario):
            resultado["mensaje"] = (
                f"{usuario.nombre} no tiene MP suficiente para {self.nombre}. "
                f"(Necesita {self.costo_mp} MP, tiene {usuario.mp} MP)"
            )
            return resultado

        # Consumir MP
        usuario.mp = max(0, usuario.mp - self.costo_mp)

        # ── ATAQUE NORMAL ──────────────────────────────────────────────────
        if self.tipo == "ataque":
            precision_efectiva = min(1.0, usuario.precision * self.precision_mod)
            if random.random() > precision_efectiva:
                resultado["mensaje"] = f"{usuario.nombre} usó {self.nombre} pero falló."
                return resultado

            dano_base = random.randint(
                int(usuario.atk * self.potencia * 0.85),
                int(usuario.atk * self.potencia * 1.15),
            )
            mult_tipo = usuario.tipo.calcular_multiplicador(objetivo.tipo)
            dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - objetivo.defensa // 2)

            objetivo.hp = max(0, objetivo.hp - dano_final)
            resultado.update({"conectó": True, "daño": dano_final})
            resultado["mensaje"] = (
                f"{usuario.nombre} usó {self.nombre} → {dano_final} de daño "
                f"a {objetivo.nombre} (tipo ×{mult_tipo:.2f})."
            )

        # ── ATAQUE ESPECIAL ────────────────────────────────────────────────
        elif self.tipo == "especial":
            precision_efectiva = min(1.0, usuario.precision * self.precision_mod)
            if random.random() > precision_efectiva:
                resultado["mensaje"] = f"{usuario.nombre} usó {self.nombre} pero falló."
                return resultado

            dano_base = random.randint(
                int(usuario.atk * self.potencia * 0.90),
                int(usuario.atk * self.potencia * 1.10),
            )
            mult_tipo = usuario.tipo.calcular_multiplicador(objetivo.tipo)
            # Especiales penetran un 70% de la DEF del objetivo
            dano_final = max(1, int(dano_base * mult_tipo * mod_clima) - int(objetivo.defensa * 0.30))

            objetivo.hp = max(0, objetivo.hp - dano_final)
            resultado.update({"conectó": True, "daño": dano_final})
            resultado["mensaje"] = (
                f"⚡ {usuario.nombre} usó {self.nombre} [ESPECIAL] → {dano_final} de daño "
                f"a {objetivo.nombre} (ignora parte de la DEF)."
            )

        # ── ESQUIVAR ───────────────────────────────────────────────────────
        elif self.tipo == "esquivar":
            # Marca al usuario en modo evasivo este turno
            usuario._evasivo = True
            resultado.update({"conectó": True, "evasión": True})
            resultado["mensaje"] = (
                f"💨 {usuario.nombre} usó {self.nombre}: "
                f"los ataques que reciba este turno tienen -50% de probabilidad de conectar."
            )

        # ── SOPORTE ────────────────────────────────────────────────────────
        elif self.tipo == "soporte":
            curacion = int(usuario.hp_max * self.potencia)
            usuario.hp = min(usuario.hp_max, usuario.hp + curacion)
            resultado.update({"conectó": True, "curación": curacion})
            resultado["mensaje"] = (
                f"💚 {usuario.nombre} usó {self.nombre}: recuperó {curacion} HP. "
                f"({usuario.hp}/{usuario.hp_max})"
            )

        return resultado

    # ─────────────────────────────────────────
    # REPRESENTACIÓN
    # ─────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Habilidad(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"costo_mp={self.costo_mp}, potencia={self.potencia})"
        )

    def __str__(self) -> str:
        return (
            f"{self.icono} {self.nombre} [{self.tipo.upper()}] "
            f"MP:{self.costo_mp} | POT:{self.potencia:.1f}x — {self.descripcion}"
        )


# ─────────────────────────────────────────
# CATÁLOGO DE HABILIDADES
# ─────────────────────────────────────────
# Estructura: nombre → Habilidad instanciada.
# Se importa desde criatura.py y game_state.py para asignar habilidades
# a criaturas en el catálogo y durante la evolución.

CATALOGO_HABILIDADES: dict[str, Habilidad] = {
    # ── Básicas (todas las criaturas en forma base) ──────────────────────
    "Atacar": Habilidad(
        nombre="Atacar",
        tipo="ataque",
        costo_mp=0,
        potencia=1.0,
        descripcion="Ataque físico básico.",
        icono="⚔",
    ),

    # ── Ignis (Fuego) ────────────────────────────────────────────────────
    "Llamarada": Habilidad(
        nombre="Llamarada",
        tipo="ataque",
        costo_mp=10,
        potencia=1.4,
        precision_mod=0.95,
        descripcion="Ataque de fuego de mediana potencia.",
        icono="🔥",
    ),
    "Colmillo Ígneo": Habilidad(
        nombre="Colmillo Ígneo",
        tipo="especial",
        costo_mp=20,
        potencia=1.8,
        precision_mod=0.88,
        descripcion="Mordida envuelta en llamas. Ignora parte de la defensa.",
        icono="🔥",
    ),
    "Erupción Solar": Habilidad(
        nombre="Erupción Solar",
        tipo="especial",
        costo_mp=35,
        potencia=2.6,
        precision_mod=0.80,
        descripcion="Explosión de plasma incandescente. Solo disponible en forma Magna.",
        icono="☀",
    ),

    # ── Torrente (Agua) ──────────────────────────────────────────────────
    "Chorro de Agua": Habilidad(
        nombre="Chorro de Agua",
        tipo="ataque",
        costo_mp=10,
        potencia=1.4,
        precision_mod=0.95,
        descripcion="Disparo de agua a presión.",
        icono="💧",
    ),
    "Vórtice": Habilidad(
        nombre="Vórtice",
        tipo="especial",
        costo_mp=22,
        potencia=1.9,
        precision_mod=0.85,
        descripcion="Torbellino de agua que arrastra al objetivo. Penetra defensa.",
        icono="🌊",
    ),
    "Marea Abismal": Habilidad(
        nombre="Marea Abismal",
        tipo="especial",
        costo_mp=38,
        potencia=2.7,
        precision_mod=0.78,
        descripcion="Oleada colosal desde las profundidades. Solo en forma Magna.",
        icono="🌊",
    ),

    # ── Rocafer (Tierra) ────────────────────────────────────────────────
    "Pedrada": Habilidad(
        nombre="Pedrada",
        tipo="ataque",
        costo_mp=10,
        potencia=1.3,
        precision_mod=0.98,
        descripcion="Lanza una roca sólida. Alta precisión.",
        icono="🪨",
    ),
    "Terremoto Menor": Habilidad(
        nombre="Terremoto Menor",
        tipo="especial",
        costo_mp=20,
        potencia=1.7,
        precision_mod=0.90,
        descripcion="Sacudida sísmica localizada. Penetra la defensa.",
        icono="🪨",
    ),
    "Colapso Tectónico": Habilidad(
        nombre="Colapso Tectónico",
        tipo="especial",
        costo_mp=40,
        potencia=2.5,
        precision_mod=0.82,
        descripcion="El suelo se rompe bajo el objetivo. Solo en forma Magna.",
        icono="⛰",
    ),

    # ── Habilidades de esquiva y soporte (universales) ───────────────────
    "Paso Sombra": Habilidad(
        nombre="Paso Sombra",
        tipo="esquivar",
        costo_mp=15,
        potencia=0.0,
        descripcion="Se funde con las sombras. Los ataques este turno tienen -50% de acierto.",
        icono="💨",
    ),
    "Aura de Tormenta": Habilidad(
        nombre="Aura de Tormenta",
        tipo="esquivar",
        costo_mp=20,
        potencia=0.0,
        descripcion="Genera un campo eléctrico disuasorio. Desvía ataques este turno.",
        icono="⚡",
    ),
    "Brisa Curativa": Habilidad(
        nombre="Brisa Curativa",
        tipo="soporte",
        costo_mp=18,
        potencia=0.25,
        descripcion="Recupera el 25% del HP máximo.",
        icono="💚",
    ),
    "Pulso Vital": Habilidad(
        nombre="Pulso Vital",
        tipo="soporte",
        costo_mp=30,
        potencia=0.40,
        descripcion="Regeneración profunda. Recupera el 40% del HP máximo.",
        icono="💚",
    ),
}