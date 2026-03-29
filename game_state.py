import random

CRIATURAS = {
    "Ignis":   {"tipo": "Fuego",  "hp": 100, "atk": 50},
    "Torrente":{"tipo": "Agua",   "hp": 110, "atk": 45},
    "Rocafer": {"tipo": "Tierra", "hp": 130, "atk": 40},
    "Voltex":  {"tipo": "Rayo",   "hp": 90,  "atk": 60},
}

MAPA = {
    "Pradera":  {"norte": "Volcán",  "este": "Lago"},
    "Volcán":   {"sur": "Pradera"},
    "Lago":     {"oeste": "Pradera"},
}

ZONAS = {
    "Pradera": ["Ignis", "Torrente"],
    "Volcán":  ["Ignis", "Rocafer"],
    "Lago":    ["Torrente", "Voltex"],
}

# ==========================
# CLASE CRIATURA
# ==========================

class Criatura:
    def __init__(self, nombre):
        data = CRIATURAS[nombre]
        self.nombre = nombre
        self.tipo = data["tipo"]
        self.hp = data["hp"]
        self.atk = data["atk"]

    def atacar(self, otro):
        daño = random.randint(int(self.atk * 0.8), int(self.atk * 1.2))
        otro.hp -= daño
        print(f"{self.nombre} hace {daño} de daño a {otro.nombre}")

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
        self.posicion = "Pradera"
        self.equipo = [Criatura("Ignis")]

    def mover(self):
        zona = MAPA[self.posicion]
        opciones = list(zona.keys())

        print(f"\nEstás en {self.posicion}")
        elec = menu(opciones)

        direccion = opciones[elec - 1]
        self.posicion = zona[direccion]
        print(f"Te moviste a {self.posicion}")

    def encuentro(self):
        if random.random() < 0.6:
            nombre = random.choice(ZONAS[self.posicion])
            enemigo = Criatura(nombre)

            print(f"\n¡Apareció {enemigo.nombre}!")

            self.batalla(self.equipo[0], enemigo)

    def batalla(self, jugador, enemigo):
        while jugador.hp > 0 and enemigo.hp > 0:
            print(f"\n{jugador.nombre} HP:{jugador.hp}")
            print(f"{enemigo.nombre} HP:{enemigo.hp}")

            menu(["Atacar"])
            jugador.atacar(enemigo)

            if enemigo.hp > 0:
                enemigo.atacar(jugador)

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