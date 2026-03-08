class GameState:
    """Datos centrales del juego. Reemplaza con tus propios objetos de dominio."""

    def __init__(self):
        self.player_name = ""
        self.gold = 100
        self.creatures = []          # Lista de objetos Criatura
        self.inventory = []          # Lista de objetos Item
        self.active_creature = None  # Criatura seleccionada para combate

        # Datos de ejemplo — reemplaza con tus clases reales
        self._load_demo_data()

    def _load_demo_data(self):
        self.creatures = [
            {
                "name": "Ignaroth",
                "type": "Fuego",
                "level": 12,
                "hp": 85, "max_hp": 120,
                "mp": 40, "max_mp": 60,
                "atk": 32, "def_": 18, "spd": 24,
                "status": "Quemado",
                "xp": 680, "xp_next": 1000,
                "color": "#E67E22",
                "icon": "🔥",
                "skills": ["Llamarada", "Colmillo Ígneo", "Rugido"],
            },
            {
                "name": "Frostmaw",
                "type": "Hielo",
                "level": 9,
                "hp": 110, "max_hp": 110,
                "mp": 55, "max_mp": 80,
                "atk": 22, "def_": 26, "spd": 16,
                "status": None,
                "xp": 320, "xp_next": 800,
                "color": "#2980B9",
                "icon": "❄️",
                "skills": ["Tormenta Gélida", "Barrera de Hielo", "Mordida Fría"],
            },
            {
                "name": "Umbrafel",
                "type": "Sombra",
                "level": 15,
                "hp": 60, "max_hp": 95,
                "mp": 90, "max_mp": 100,
                "atk": 40, "def_": 12, "spd": 38,
                "status": "Maldito",
                "xp": 1200, "xp_next": 1500,
                "color": "#9B59B6",
                "icon": "🌑",
                "skills": ["Sombra Cortante", "Maldición", "Paso Sombrío"],
            },
        ]
        self.active_creature = self.creatures[0]

        self.inventory = [
            {"name": "Poción Mayor", "type": "Consumible", "qty": 3,
             "desc": "Restaura 80 HP a una criatura.", "price": 150, "icon": "🧪"},
            {"name": "Éter Oscuro",  "type": "Consumible", "qty": 1,
             "desc": "Restaura 50 MP. Puede enfermar.", "price": 200, "icon": "💧"},
            {"name": "Runa de Fuego","type": "Runa",       "qty": 2,
             "desc": "Aumenta ATK +15 por 3 turnos.",  "price": 300, "icon": "📜"},
            {"name": "Amuleto Roto", "type": "Accesorio",  "qty": 1,
             "desc": "Reduce daño recibido un 10%.",   "price": 500, "icon": "💎"},
            {"name": "Polvo Lunar",  "type": "Material",   "qty": 5,
             "desc": "Ingrediente para evolución.",     "price": 80,  "icon": "✨"},
        ]

    SHOP_ITEMS = [
        {"name": "Poción Mayor",   "type": "Consumible", "price": 150,
         "desc": "Restaura 80 HP.", "icon": "🧪"},
        {"name": "Éter Oscuro",    "type": "Consumible", "price": 200,
         "desc": "Restaura 50 MP.", "icon": "💧"},
        {"name": "Runa de Fuego",  "type": "Runa",       "price": 300,
         "desc": "+15 ATK por 3 turnos.", "icon": "📜"},
        {"name": "Runa de Hielo",  "type": "Runa",       "price": 300,
         "desc": "+15 DEF por 3 turnos.", "icon": "📜"},
        {"name": "Polvo Lunar",    "type": "Material",   "price": 80,
         "desc": "Material de evolución.", "icon": "✨"},
        {"name": "Amuleto Roto",   "type": "Accesorio",  "price": 500,
         "desc": "Reduce daño recibido.", "icon": "💎"},
        {"name": "Tónico de Fuerza","type": "Consumible","price": 250,
         "desc": "+20 ATK permanente.", "icon": "⚗️"},
        {"name": "Cristal de Alma", "type": "Material",  "price": 1000,
         "desc": "Permite cruzar criaturas.", "icon": "🔮"},
    ]
