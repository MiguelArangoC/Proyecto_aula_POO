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
# CLASE CONDICION CLIMATICA
# ==========================

class CondicionClimatica:
    """Modifica el combate segun el clima activo en la zona."""

    def __init__(self, nombre: str):
        data = DATOS_CLIMA[nombre]
        self.nombre = nombre
        self.beneficia = data["beneficia"]
        self.perjudica = data["perjudica"]
        self.dano_turno = data["dano_turno"]  # {"Fuego": 5, ...}

    def modificador_ataque(self, tipo: str) -> float:
        """Devuelve 1.20 si el tipo es beneficiado, 0.90 si es perjudicado, 1.0 si neutro."""
        if tipo in self.beneficia:
            return 1.20
        if tipo in self.perjudica:
            return 0.90
        return 1.0

    def aplicar_dano_turno(self, criatura) -> int:
        """Aplica dano por turno si el clima lo indica. Retorna el dano aplicado."""
        dano = self.dano_turno.get(criatura.tipo, 0)
        criatura.hp -= dano
        return dano
    
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



from dataclasses import dataclass


@dataclass
class Item:
    nombre: str
    descripcion: str
    modificador_hp: int   
    modificador_atk: int 

    def modificar_estadistica(self, criatura):
        """Aplica las estadísticas directamente, sin importar el tipo de ítem."""
        print(f"\n[!] Usando {self.nombre} en {criatura.nombre}...")
        print(f"[{self.descripcion}]")

        
        criatura.hp += self.modificador_hp
        
       
        nuevo_atk = criatura.atk + self.modificador_atk
        criatura.atk = max(1, nuevo_atk) 

      
        if self.modificador_hp != 0:
            accion_hp = "recupera" if self.modificador_hp > 0 else "pierde"
            print(f"  > {criatura.nombre} {accion_hp} {abs(self.modificador_hp)} HP.")
            
        if self.modificador_atk != 0:
            accion_atk = "aumenta" if self.modificador_atk > 0 else "reduce"
            print(f"  > {criatura.nombre} {accion_atk} su Ataque en {abs(self.modificador_atk)}.")



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