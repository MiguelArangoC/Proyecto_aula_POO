import random
from criatura import Criatura

CRIATURAS = {
    "Ignis":   {"tipo": "Fuego",  "hp": 100, "atk": 50},
    "Torrente":{"tipo": "Agua",   "hp": 110, "atk": 45},
    "Rocafer": {"tipo": "Tierra", "hp": 130, "atk": 40},
    "Voltex":  {"tipo": "Rayo",   "hp": 90,  "atk": 60},
}

from mapa import Mapa

# ─────────────────────────
# HELPERS CONSOLA
# ─────────────────────────

def menu(opciones):
    for i, op in enumerate(opciones, 1):
        print(f"[{i}] {op}")
    while True:
        try:
            op = int(input("Opción: "))
            if 1 <= op <= len(opciones):
                return op
        except:
            pass

# ─────────────────────────
# JUEGO
# ─────────────────────────

class Juego:
    def __init__(self):
        self.mapa = Mapa.crear_mapa_default()
        self.posicion = "Pradera"
        data = CRIATURAS["Ignis"]
        self.equipo = [Criatura(nombre="Ignis", tipo=data["tipo"], hp=data["hp"], atk=data["atk"])]

    def mover(self):
        zona = self.mapa.obtener_zona(self.posicion)
        opciones = list(zona.conexiones.keys())

        print(f"\nEstás en {self.posicion}")
        elec = menu(opciones)

        direccion = opciones[elec - 1]
        self.posicion = zona.conexiones[direccion]
        print(f"Te moviste a {self.posicion}")

    def encuentro(self):
        if random.random() < 0.6:
            zona = self.mapa.obtener_zona(self.posicion)
            nombre = zona.obtener_criatura_aleatoria()
            if not nombre:
                return
            data = CRIATURAS[nombre]
            enemigo = Criatura(nombre=nombre, tipo=data["tipo"], hp=data["hp"], atk=data["atk"])

            print(f"\n¡Apareció {enemigo.nombre}!")

            self.batalla(self.equipo[0], enemigo)

    def batalla(self, jugador, enemigo):
        while jugador.hp > 0 and enemigo.hp > 0:
            print(f"\n{jugador.nombre} HP:{jugador.hp}/{jugador.hp_max}")
            print(f"{enemigo.nombre} HP:{enemigo.hp}/{enemigo.hp_max}")

            menu(["Atacar"])
            
            conecto, dano = jugador.atacar(enemigo)
            if conecto:
                print(f"{jugador.nombre} hace {dano} de daño a {enemigo.nombre}")
            else:
                print(f"¡El ataque de {jugador.nombre} falló!")

            if enemigo.hp > 0:
                conecto, dano = enemigo.atacar(jugador)
                if conecto:
                    print(f"{enemigo.nombre} hace {dano} de daño a {jugador.nombre}")
                else:
                    print(f"¡El ataque de {enemigo.nombre} falló!")

        if jugador.hp > 0:
            print("¡Ganaste!")
        else:
            print("Perdiste...")

# ─────────────────────────
# MAIN
# ─────────────────────────

def main():
    juego = Juego()

    while True:
        print("\n--- MENÚ ---")
        op = menu(["Mover", "Explorar", "Salir"])

        if op == 1:
            juego.mover()
        elif op == 2:
            juego.encuentro()
        else:
            break

if __name__ == "__main__":
    main()