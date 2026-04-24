"""
test_us02.py
============
Script de verificacion de importaciones e integracion basica para US-02.
"""
from excepciones import (
    EquipoLlenoError, CapturaFallidaError, ItemNoDisponibleError,
    CriaturaDebilitadaError, PartidaNoEncontradaError, ZonaInexistenteError
)
from tipo import Tipo
from item import Item
from criatura import Criatura
from jugador import Jugador
from mapa import Zona, Mapa
from condicion_climatica import CondicionClimatica
from batalla import Batalla, EstadoBatalla

print("=== VERIFICACION DE IMPORTACIONES ===")
print("excepciones.py         OK")
print("tipo.py                OK")
print("item.py                OK")
print("criatura.py            OK")
print("jugador.py             OK")
print("mapa.py                OK")
print("condicion_climatica.py OK")
print("batalla.py             OK")

# ── Tipos ──
fuego = Tipo("Fuego")
tierra = Tipo("Tierra")
agua = Tipo("Agua")
assert fuego.calcular_multiplicador(tierra) == 1.5
assert agua.calcular_multiplicador(fuego) == 1.5
print()
print("=== TEST TIPO ===")
print(f"Fuego vs Tierra: x{fuego.calcular_multiplicador(tierra)}  (esperado: 1.5)")
print(f"Agua vs Fuego:   x{agua.calcular_multiplicador(fuego)}   (esperado: 1.5)")

# ── Criatura ──
ignis = Criatura("Ignis", "Fuego", 100, 50, defensa=15, velocidad=12)
print()
print("=== TEST CRIATURA ===")
print(ignis)

# ── Jugador ──
jugador = Jugador("Ash")
jugador.agregar_criatura(ignis)
pocion = Item(
    nombre="Pocion",
    descripcion="Restaura 30 HP",
    efecto_positivo={"hp": 30},
    efecto_negativo={},
    es_consumible=True,
)
jugador.agregar_item(pocion)
print()
print("=== TEST JUGADOR ===")
print(jugador)

# ── Mapa ──
mapa = Mapa.crear_mapa_default()
print()
print("=== TEST MAPA ===")
print(mapa)

# ── Clima ──
clima = CondicionClimatica("Lluvioso")
print()
print("=== TEST CLIMA ===")
print(clima)

# ── Batalla (1 turno) ──
enemigo = Criatura("Torrente", "Agua", 110, 45, defensa=12)
batalla = Batalla(jugador, enemigo, nombre_clima="Lluvioso")
estado = batalla.ejecutar_turno()
print()
print("=== TEST BATALLA (1 turno) ===")
print(batalla.resumen())
print()
for evento in batalla.log:
    print(" ", evento)

print()
print("=== TODOS LOS MODULOS VERIFICADOS CORRECTAMENTE ===")
