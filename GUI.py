"""
RPG GUI - Dark Fantasy Edition
================================
GUI modular construida con Tkinter para un juego RPG.
Cada pantalla está diseñada para conectarse fácilmente a tu lógica de backend.

CÓMO CONECTAR TU BACKEND:
- Busca los comentarios "# BACKEND:" en cada método para saber dónde inyectar tu lógica.
- La clase `GameState` centraliza todos los datos del juego.
- Las pantallas llaman a métodos del controlador principal `RPGApp`.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import math


# ══════════════════════════════════════════════════════════════
#  PALETA DE COLORES — Dark Fantasy
# ══════════════════════════════════════════════════════════════
C = {
    "bg_dark":      "#0A0A0F",
    "bg_panel":     "#111118",
    "bg_card":      "#1A1A26",
    "bg_hover":     "#222235",
    "border":       "#2A2A45",
    "border_gold":  "#8B6914",
    "gold":         "#C9A227",
    "gold_light":   "#F0C040",
    "red":          "#C0392B",
    "red_light":    "#E74C3C",
    "blue":         "#1A6FAA",
    "blue_light":   "#3498DB",
    "green":        "#1A7A3A",
    "green_light":  "#2ECC71",
    "purple":       "#6C3483",
    "purple_light": "#9B59B6",
    "frost":        "#2980B9",
    "flame":        "#E67E22",
    "text_bright":  "#F0EAD6",
    "text_mid":     "#A09070",
    "text_dim":     "#605040",
    "hp_bar":       "#8B0000",
    "hp_fill":      "#CC2200",
    "mp_bar":       "#00008B",
    "mp_fill":      "#0044CC",
    "xp_fill":      "#8B6914",
}

FONTS = {
    "title":    ("Georgia", 26, "bold"),
    "subtitle": ("Georgia", 16, "bold italic"),
    "heading":  ("Georgia", 13, "bold"),
    "body":     ("Courier", 11),
    "body_sm":  ("Courier", 9),
    "btn":      ("Georgia", 11, "bold"),
    "btn_sm":   ("Georgia", 9, "bold"),
    "stat":     ("Courier", 10, "bold"),
    "big_num":  ("Courier", 18, "bold"),
    "lore":     ("Georgia", 10, "italic"),
}


from game_state import GameState


# ══════════════════════════════════════════════════════════════
#  WIDGETS REUTILIZABLES
# ══════════════════════════════════════════════════════════════
class DarkButton(tk.Button):
    def __init__(self, parent, text, command=None, accent=C["gold"],
                 width=None, pady=8, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            bg=C["bg_card"], fg=accent,
            activebackground=C["bg_hover"], activeforeground=C["gold_light"],
            relief="flat", bd=0, cursor="hand2",
            font=FONTS["btn"], pady=pady,
            **({} if width is None else {"width": width}),
            **kwargs,
        )
        self.accent = accent
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=C["bg_hover"], fg=C["gold_light"])

    def _on_leave(self, _):
        self.config(bg=C["bg_card"], fg=self.accent)


class StatBar(tk.Canvas):
    """Barra de estadística animada (HP / MP / XP)."""
    def __init__(self, parent, fill_color, bg_color=C["bg_panel"],
                 height=12, width=200, **kwargs):
        super().__init__(parent, height=height, width=width,
                         bg=C["bg_panel"], highlightthickness=0, **kwargs)
        self._fill = fill_color
        self.bar_width = width
        self.bar_height = height
        self._ratio = 1.0
        self._draw()

    def set_ratio(self, ratio):
        self._ratio = max(0.0, min(1.0, ratio))
        self._draw()

    def _draw(self):
        self.delete("all")
        self.create_rectangle(0, 0, self.bar_width, self.bar_height,
                               fill=C["bg_dark"], outline=C["border"])
        w = int(self.bar_width * self._ratio)
        if w > 2:
            self.create_rectangle(2, 2, w - 2, self.bar_height - 2,
                                   fill=self._fill, outline="")


class SeparatorLine(tk.Frame):
    def __init__(self, parent, color=C["border_gold"], **kwargs):
        super().__init__(parent, bg=color, height=1, **kwargs)


def panel(parent, padx=12, pady=10, **kwargs):
    f = tk.Frame(parent, bg=C["bg_card"], **kwargs)
    f.pack(fill="x", padx=padx, pady=pady)
    return f


def label(parent, text, font=FONTS["body"], fg=C["text_bright"],
          bg=C["bg_card"], anchor="w", **kwargs):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg,
                    anchor=anchor, **kwargs)


# ══════════════════════════════════════════════════════════════
#  PANTALLA: INICIO / CREAR JUGADOR
# ══════════════════════════════════════════════════════════════
class StartScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Fondo con patrón de puntos simulado
        canvas = tk.Canvas(self, bg=C["bg_dark"], highlightthickness=0)
        canvas.place(relwidth=1, relheight=1)
        self._draw_bg(canvas)

        # Contenedor central
        box = tk.Frame(self, bg=C["bg_panel"],
                       highlightbackground=C["border_gold"],
                       highlightthickness=1)
        box.place(relx=0.5, rely=0.5, anchor="center", width=480, height=520)

        # Ornamento superior
        ornament = tk.Canvas(box, width=460, height=30,
                              bg=C["bg_panel"], highlightthickness=0)
        ornament.pack(pady=(18, 0))
        self._draw_ornament(ornament)

        tk.Label(box, text="⚔  CHRONICLE OF SHADOWS  ⚔",
                 font=("Georgia", 18, "bold"), fg=C["gold"],
                 bg=C["bg_panel"]).pack(pady=(8, 0))

        tk.Label(box, text="Un reino sumido en la oscuridad te espera...",
                 font=FONTS["lore"], fg=C["text_mid"], bg=C["bg_panel"]).pack()

        SeparatorLine(box, padx=40).pack(fill="x", padx=40, pady=14)

        # Formulario
        tk.Label(box, text="NOMBRE DEL AVENTURERO",
                 font=FONTS["btn_sm"], fg=C["text_dim"],
                 bg=C["bg_panel"]).pack()

        self.name_var = tk.StringVar()
        entry = tk.Entry(box, textvariable=self.name_var,
                         font=("Georgia", 14), fg=C["text_bright"],
                         bg=C["bg_card"], insertbackground=C["gold"],
                         relief="flat", bd=0, justify="center")
        entry.pack(ipady=10, padx=60, fill="x", pady=(6, 0))
        tk.Frame(box, bg=C["border_gold"], height=1).pack(fill="x", padx=60)

        entry.bind("<Return>", lambda _: self._start())

        # Botón inicio
        tk.Frame(box, bg=C["bg_panel"], height=20).pack()

        start_btn = tk.Button(
            box,
            text="⚔   COMENZAR AVENTURA   ⚔",
            command=self._start,
            bg=C["border_gold"], fg=C["bg_dark"],
            activebackground=C["gold"], activeforeground=C["bg_dark"],
            font=("Georgia", 13, "bold"), relief="flat", bd=0,
            pady=14, cursor="hand2",
        )
        start_btn.pack(padx=50, fill="x")

        SeparatorLine(box, padx=40).pack(fill="x", padx=40, pady=16)

        lore = (
            "En las tierras de Aethermoor, criaturas de sombra y llama\n"
            "aguardan ser domadas por un maestro digno.\n"
            "¿Será ese maestro... tú?"
        )
        tk.Label(box, text=lore, font=FONTS["lore"],
                 fg=C["text_dim"], bg=C["bg_panel"],
                 justify="center").pack()

    def _draw_bg(self, canvas):
        canvas.update_idletasks()
        w, h = 1280, 800
        for _ in range(120):
            x, y = random.randint(0, w), random.randint(0, h)
            r = random.choice([1, 1, 1, 2])
            alpha_color = random.choice([C["border"], C["text_dim"], C["border_gold"]])
            canvas.create_oval(x, y, x+r, y+r, fill=alpha_color, outline="")

    def _draw_ornament(self, canvas):
        w = 460
        canvas.create_line(10, 15, w-10, 15, fill=C["border_gold"], width=1)
        for x in [w//2 - 60, w//2, w//2 + 60]:
            canvas.create_oval(x-3, 12, x+3, 18,
                                fill=C["gold"], outline="")

    def _start(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Nombre requerido",
                                   "Debes ingresar el nombre de tu aventurero.")
            return
        # BACKEND: llama aquí a tu método de creación de jugador
        # Ejemplo: self.app.backend.create_player(name)
        self.app.state.player_name = name
        self.app.show_screen("main")


# ══════════════════════════════════════════════════════════════
#  BARRA LATERAL DE NAVEGACIÓN
# ══════════════════════════════════════════════════════════════
class SideNav(tk.Frame):
    TABS = [
        ("🐉", "Criaturas",  "creatures"),
        ("⚔️",  "Combate",    "combat"),
        ("🎒", "Inventario", "inventory"),
        ("🏪", "Tienda",     "shop"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_panel"], width=72)
        self.app = app
        self.pack_propagate(False)
        self._buttons = {}
        self._build()

    def _build(self):
        # Logo
        tk.Label(self, text="⚔", font=("Georgia", 22),
                 fg=C["gold"], bg=C["bg_panel"]).pack(pady=(18, 4))
        SeparatorLine(self).pack(fill="x", padx=8, pady=6)

        for icon, name, key in self.TABS:
            btn = tk.Button(
                self, text=f"{icon}\n{name}",
                command=lambda k=key: self.master.show(k),
                bg=C["bg_panel"], fg=C["text_mid"],
                activebackground=C["bg_card"], activeforeground=C["gold"],
                font=FONTS["body_sm"], relief="flat", bd=0,
                pady=10, cursor="hand2", width=8,
            )
            btn.pack(fill="x", padx=4, pady=2)
            self._buttons[key] = btn

        # Espacio + info jugador abajo
        tk.Frame(self, bg=C["bg_panel"]).pack(expand=True)
        SeparatorLine(self).pack(fill="x", padx=8, pady=6)
        self.gold_label = tk.Label(self, text="💰\n—",
                                    font=FONTS["body_sm"],
                                    fg=C["gold"], bg=C["bg_panel"])
        self.gold_label.pack(pady=(0, 12))

    def set_active(self, key):
        for k, btn in self._buttons.items():
            if k == key:
                btn.config(bg=C["bg_card"], fg=C["gold"])
            else:
                btn.config(bg=C["bg_panel"], fg=C["text_mid"])

    def refresh_gold(self, amount):
        self.gold_label.config(text=f"💰\n{amount}g")


# ══════════════════════════════════════════════════════════════
#  PANTALLA: GESTIÓN DE CRIATURAS
# ══════════════════════════════════════════════════════════════
class CreaturesScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self._selected = None
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["bg_panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="  🐉  CRIATURAS CAPTURADAS",
                 font=FONTS["subtitle"], fg=C["gold"],
                 bg=C["bg_panel"]).pack(side="left", pady=12, padx=8)

        # Layout: lista izq | detalle der
        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Lista
        left = tk.Frame(body, bg=C["bg_panel"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 8))

        tk.Label(left, text="MIS CRIATURAS", font=FONTS["btn_sm"],
                 fg=C["text_dim"], bg=C["bg_panel"]).pack(pady=8)

        self.list_frame = tk.Frame(left, bg=C["bg_panel"])
        self.list_frame.pack(fill="both", expand=True, padx=6)

        # Detalle
        self.detail_frame = tk.Frame(body, bg=C["bg_panel"],
                                      highlightbackground=C["border"],
                                      highlightthickness=1)
        self.detail_frame.pack(side="left", fill="both", expand=True)

        self._refresh_list()
        if self.app.state.creatures:
            self._show_detail(self.app.state.creatures[0])

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for c in self.app.state.creatures:
            self._make_list_card(c)

    def _make_list_card(self, creature):
        bg = C["bg_card"]
        card = tk.Frame(self.list_frame, bg=bg, cursor="hand2",
                         highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=3)

        icon_lbl = tk.Label(card, text=creature["icon"], font=("", 22),
                             bg=bg, fg=creature["color"])
        icon_lbl.pack(side="left", padx=8, pady=6)

        info = tk.Frame(card, bg=bg)
        info.pack(side="left", fill="x", expand=True, pady=4)
        tk.Label(info, text=creature["name"], font=FONTS["heading"],
                 fg=C["text_bright"], bg=bg, anchor="w").pack(fill="x")
        tk.Label(info, text=f"Nv.{creature['level']}  {creature['type']}",
                 font=FONTS["body_sm"], fg=C["text_mid"], bg=bg,
                 anchor="w").pack(fill="x")

        hp_bar = StatBar(card, C["hp_fill"], height=6, width=80)
        hp_bar.pack(side="right", padx=8)
        hp_bar.set_ratio(creature["hp"] / creature["max_hp"])

        for w in (card, icon_lbl, info):
            w.bind("<Button-1>", lambda _, c=creature: self._show_detail(c))
        for child in info.winfo_children():
            child.bind("<Button-1>", lambda _, c=creature: self._show_detail(c))

    def _show_detail(self, creature):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        bg = C["bg_panel"]
        c = creature

        # Nombre + icono
        top = tk.Frame(self.detail_frame, bg=bg)
        top.pack(fill="x", padx=16, pady=(16, 4))
        tk.Label(top, text=c["icon"], font=("", 48),
                 fg=c["color"], bg=bg).pack(side="left")
        info_top = tk.Frame(top, bg=bg)
        info_top.pack(side="left", padx=16)
        tk.Label(info_top, text=c["name"], font=FONTS["title"],
                 fg=c["color"], bg=bg, anchor="w").pack(fill="x")
        tk.Label(info_top, text=f"Tipo: {c['type']}   •   Nivel {c['level']}",
                 font=FONTS["body"], fg=C["text_mid"], bg=bg, anchor="w").pack(fill="x")

        status_txt = f"Estado: {c['status']}" if c["status"] else "Estado: Normal"
        status_col = C["red_light"] if c["status"] else C["green_light"]
        tk.Label(info_top, text=status_txt, font=FONTS["body_sm"],
                 fg=status_col, bg=bg, anchor="w").pack(fill="x")

        SeparatorLine(self.detail_frame).pack(fill="x", padx=16, pady=8)

        # Barras HP / MP / XP
        bars = tk.Frame(self.detail_frame, bg=bg)
        bars.pack(fill="x", padx=20)

        def stat_row(parent, label_text, cur, mx, fill_c):
            row = tk.Frame(parent, bg=bg)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label_text, font=FONTS["stat"],
                     fg=C["text_mid"], bg=bg, width=4, anchor="w").pack(side="left")
            bar = StatBar(row, fill_c, width=220, height=14)
            bar.pack(side="left", padx=6)
            bar.set_ratio(cur / mx if mx else 0)
            tk.Label(row, text=f"{cur}/{mx}", font=FONTS["body_sm"],
                     fg=C["text_mid"], bg=bg).pack(side="left")

        stat_row(bars, "HP", c["hp"], c["max_hp"], C["hp_fill"])
        stat_row(bars, "MP", c["mp"], c["max_mp"], C["mp_fill"])
        stat_row(bars, "XP", c["xp"], c["xp_next"], C["xp_fill"])

        SeparatorLine(self.detail_frame).pack(fill="x", padx=16, pady=8)

        # Stats
        stats_frame = tk.Frame(self.detail_frame, bg=bg)
        stats_frame.pack(fill="x", padx=20)
        tk.Label(stats_frame, text="ESTADÍSTICAS BASE",
                 font=FONTS["btn_sm"], fg=C["text_dim"], bg=bg,
                 anchor="w").pack(fill="x", pady=(0, 6))

        stats_row = tk.Frame(stats_frame, bg=bg)
        stats_row.pack(fill="x")
        for stat_name, val, col in [
            ("⚔ ATK", c["atk"], C["red_light"]),
            ("🛡 DEF", c["def_"], C["blue_light"]),
            ("💨 VEL", c["spd"], C["green_light"]),
        ]:
            box = tk.Frame(stats_row, bg=C["bg_card"],
                            highlightbackground=C["border"], highlightthickness=1)
            box.pack(side="left", padx=6, pady=4, ipadx=14, ipady=8)
            tk.Label(box, text=str(val), font=FONTS["big_num"],
                     fg=col, bg=C["bg_card"]).pack()
            tk.Label(box, text=stat_name, font=FONTS["body_sm"],
                     fg=C["text_mid"], bg=C["bg_card"]).pack()

        SeparatorLine(self.detail_frame).pack(fill="x", padx=16, pady=8)

        # Habilidades
        tk.Label(self.detail_frame, text="HABILIDADES",
                 font=FONTS["btn_sm"], fg=C["text_dim"],
                 bg=bg, anchor="w").pack(fill="x", padx=20)
        skills_frame = tk.Frame(self.detail_frame, bg=bg)
        skills_frame.pack(fill="x", padx=20, pady=6)
        for skill in c.get("skills", []):
            sk_btn = tk.Label(
                skills_frame, text=f"  ✦ {skill}  ",
                font=FONTS["body_sm"], fg=c["color"],
                bg=C["bg_card"],
                highlightbackground=c["color"], highlightthickness=1,
                pady=4, padx=4,
            )
            sk_btn.pack(side="left", padx=4)

        # Botones acción
        btn_row = tk.Frame(self.detail_frame, bg=bg)
        btn_row.pack(fill="x", padx=20, pady=12)

        def make_btn(parent, text, color, cmd):
            b = tk.Button(parent, text=text, command=cmd,
                          bg=C["bg_card"], fg=color,
                          activebackground=C["bg_hover"], activeforeground=color,
                          font=FONTS["btn_sm"], relief="flat", bd=0,
                          pady=8, padx=12, cursor="hand2")
            b.pack(side="left", padx=4)

        make_btn(btn_row, "⚔ Enviar a Combate", C["gold"],
                 lambda: self._set_active(creature))
        make_btn(btn_row, "✨ Evolucionar", C["purple_light"],
                 lambda: self._evolve(creature))
        make_btn(btn_row, "🔀 Cruzar", C["green_light"],
                 lambda: self._cross(creature))

    def _set_active(self, creature):
        # BACKEND: self.app.backend.set_active_creature(creature)
        self.app.state.active_creature = creature
        messagebox.showinfo("Criatura activa",
                             f"{creature['name']} está lista para el combate.")

    def _evolve(self, creature):
        # BACKEND: self.app.backend.evolve_creature(creature)
        cost = 500
        if self.app.state.gold < cost:
            messagebox.showwarning("Oro insuficiente",
                                    f"Necesitas {cost}g para evolucionar.")
            return
        messagebox.showinfo("Evolución",
                             f"La evolución de {creature['name']} requiere "
                             f"Polvo Lunar × 2 y {cost}g.\n(Conecta tu backend aquí)")

    def _cross(self, creature):
        # BACKEND: self.app.backend.cross_creatures(creature, other)
        messagebox.showinfo("Cruce de Criaturas",
                             "Selecciona una segunda criatura para cruzar.\n"
                             "(Conecta tu backend aquí)")

    def refresh(self):
        self._refresh_list()


# ══════════════════════════════════════════════════════════════
#  PANTALLA: SISTEMA DE COMBATE
# ══════════════════════════════════════════════════════════════
class CombatScreen(tk.Frame):
    ENVIRONMENTS = ["☀ Normal", "🌧 Lluvia", "⛈ Tormenta", "❄ Nevado", "🔥 Volcánico"]
    ENEMY_POOL = [
        {"name": "Wraithling",  "type": "Sombra", "hp": 80,  "max_hp": 80,
         "atk": 18, "icon": "👻", "color": C["purple_light"], "status": None},
        {"name": "Embervore",   "type": "Fuego",  "hp": 95,  "max_hp": 95,
         "atk": 22, "icon": "🦎", "color": C["flame"],        "status": None},
        {"name": "Glaciomaw",   "type": "Hielo",  "hp": 110, "max_hp": 110,
         "atk": 16, "icon": "🐺", "color": C["frost"],        "status": None},
    ]

    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self.enemy = None
        self.environment = "☀ Normal"
        self.log_lines = []
        self.combat_active = False
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg_panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="  ⚔️  ARENA DE COMBATE",
                 font=FONTS["subtitle"], fg=C["red_light"],
                 bg=C["bg_panel"]).pack(side="left", pady=12, padx=8)

        # Selector de ambiente
        env_frame = tk.Frame(hdr, bg=C["bg_panel"])
        env_frame.pack(side="right", padx=12)
        tk.Label(env_frame, text="Ambiente:", font=FONTS["body_sm"],
                 fg=C["text_dim"], bg=C["bg_panel"]).pack(side="left")
        self.env_var = tk.StringVar(value=self.environment)
        env_menu = ttk.Combobox(env_frame, textvariable=self.env_var,
                                 values=self.ENVIRONMENTS, state="readonly",
                                 width=14, font=FONTS["body_sm"])
        env_menu.pack(side="left", padx=6)
        env_menu.bind("<<ComboboxSelected>>",
                       lambda _: self._change_env(self.env_var.get()))

        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel izquierdo: jugador vs enemigo
        arena = tk.Frame(body, bg=C["bg_panel"],
                          highlightbackground=C["border"], highlightthickness=1)
        arena.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # ── Jugador ──
        self.player_frame = tk.Frame(arena, bg=C["bg_panel"])
        self.player_frame.pack(fill="x", padx=12, pady=10)

        # ── VS ──
        tk.Label(arena, text="⚔  VS  ⚔", font=("Georgia", 14, "bold"),
                 fg=C["border_gold"], bg=C["bg_panel"]).pack()

        # ── Enemigo ──
        self.enemy_frame = tk.Frame(arena, bg=C["bg_panel"])
        self.enemy_frame.pack(fill="x", padx=12, pady=10)

        SeparatorLine(arena).pack(fill="x", padx=12, pady=6)

        # Habilidades
        tk.Label(arena, text="HABILIDADES",
                 font=FONTS["btn_sm"], fg=C["text_dim"],
                 bg=C["bg_panel"]).pack(pady=(0, 4))
        self.skills_frame = tk.Frame(arena, bg=C["bg_panel"])
        self.skills_frame.pack(pady=(0, 10))

        # Botones combate
        ctrl = tk.Frame(arena, bg=C["bg_panel"])
        ctrl.pack(pady=8)

        self.start_btn = tk.Button(
            ctrl, text="⚔ INICIAR COMBATE",
            command=self._start_combat,
            bg=C["red"], fg=C["text_bright"],
            activebackground=C["red_light"], activeforeground="white",
            font=FONTS["btn"], relief="flat", bd=0, pady=10, padx=20,
            cursor="hand2",
        )
        self.start_btn.pack(side="left", padx=6)

        self.flee_btn = tk.Button(
            ctrl, text="🏃 HUIR",
            command=self._flee,
            bg=C["bg_card"], fg=C["text_mid"],
            activebackground=C["bg_hover"], activeforeground=C["text_bright"],
            font=FONTS["btn"], relief="flat", bd=0, pady=10, padx=16,
            cursor="hand2", state="disabled",
        )
        self.flee_btn.pack(side="left", padx=6)

        # Panel derecho: log de combate
        log_panel = tk.Frame(body, bg=C["bg_panel"],
                              highlightbackground=C["border"], highlightthickness=1,
                              width=280)
        log_panel.pack(side="left", fill="both")
        log_panel.pack_propagate(False)

        tk.Label(log_panel, text="📜 REGISTRO DE COMBATE",
                 font=FONTS["btn_sm"], fg=C["text_dim"],
                 bg=C["bg_panel"]).pack(pady=8)

        self.log_text = tk.Text(
            log_panel, bg=C["bg_dark"], fg=C["text_bright"],
            font=FONTS["body_sm"], relief="flat", bd=0,
            state="disabled", wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.log_text.tag_config("gold",  foreground=C["gold"])
        self.log_text.tag_config("red",   foreground=C["red_light"])
        self.log_text.tag_config("blue",  foreground=C["blue_light"])
        self.log_text.tag_config("green", foreground=C["green_light"])
        self.log_text.tag_config("dim",   foreground=C["text_dim"])

        self._refresh_combatants()

    def _change_env(self, env):
        self.environment = env
        # BACKEND: self.app.backend.set_environment(env)
        self._log(f"El ambiente cambia a {env}.", "blue")

    def _refresh_combatants(self):
        for w in self.player_frame.winfo_children():
            w.destroy()
        for w in self.enemy_frame.winfo_children():
            w.destroy()
        for w in self.skills_frame.winfo_children():
            w.destroy()

        c = self.app.state.active_creature
        if c:
            self._combatant_widget(self.player_frame, c, is_player=True)
        else:
            tk.Label(self.player_frame,
                     text="Sin criatura activa.\nVe a Criaturas y selecciona una.",
                     font=FONTS["body"], fg=C["text_dim"],
                     bg=C["bg_panel"]).pack()

        if self.enemy:
            self._combatant_widget(self.enemy_frame, self.enemy, is_player=False)
        else:
            tk.Label(self.enemy_frame,
                     text="Inicia el combate para\nencontrar un enemigo.",
                     font=FONTS["body"], fg=C["text_dim"],
                     bg=C["bg_panel"]).pack()

        # Habilidades
        if c and self.combat_active:
            for skill in c.get("skills", []):
                sk_btn = tk.Button(
                    self.skills_frame, text=f"✦ {skill}",
                    command=lambda s=skill: self._use_skill(s),
                    bg=C["bg_card"], fg=c["color"],
                    activebackground=C["bg_hover"], activeforeground=C["gold_light"],
                    font=FONTS["btn_sm"], relief="flat", bd=0,
                    pady=8, padx=10, cursor="hand2",
                )
                sk_btn.pack(side="left", padx=4)

    def _combatant_widget(self, parent, data, is_player):
        bg = C["bg_panel"]
        side = "TU CRIATURA" if is_player else "ENEMIGO"
        tk.Label(parent, text=side, font=FONTS["btn_sm"],
                 fg=C["text_dim"], bg=bg).pack(anchor="w")

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x")
        tk.Label(row, text=data["icon"], font=("", 36),
                 fg=data["color"], bg=bg).pack(side="left", padx=8)

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=data["name"], font=FONTS["heading"],
                 fg=data["color"], bg=bg, anchor="w").pack(fill="x")

        status_txt = data.get("status") or "Normal"
        status_col = C["red_light"] if data.get("status") else C["green_light"]
        tk.Label(info, text=f"Estado: {status_txt}", font=FONTS["body_sm"],
                 fg=status_col, bg=bg, anchor="w").pack(fill="x")

        hp = data["hp"]
        max_hp = data["max_hp"]
        hp_row = tk.Frame(info, bg=bg)
        hp_row.pack(fill="x", pady=2)
        tk.Label(hp_row, text="HP", font=FONTS["stat"],
                 fg=C["text_mid"], bg=bg, width=3).pack(side="left")
        bar = StatBar(hp_row, C["hp_fill"], width=160, height=14)
        bar.pack(side="left", padx=4)
        bar.set_ratio(hp / max_hp if max_hp else 0)
        tk.Label(hp_row, text=f"{hp}/{max_hp}", font=FONTS["body_sm"],
                 fg=C["text_mid"], bg=bg).pack(side="left")

        if "atk" in data:
            tk.Label(info, text=f"⚔ ATK {data['atk']}",
                     font=FONTS["body_sm"], fg=C["text_mid"],
                     bg=bg, anchor="w").pack(fill="x")

    def _start_combat(self):
        if not self.app.state.active_creature:
            messagebox.showwarning("Sin criatura",
                                    "Selecciona una criatura activa primero.")
            return
        # BACKEND: self.enemy = self.app.backend.get_new_enemy()
        self.enemy = dict(random.choice(self.ENEMY_POOL))
        self.enemy["hp"] = self.enemy["max_hp"]
        self.combat_active = True
        self.start_btn.config(state="disabled")
        self.flee_btn.config(state="normal")
        self._log("═" * 30, "dim")
        self._log(f"¡{self.enemy['name']} aparece!", "red")
        self._log(f"Ambiente: {self.environment}", "blue")
        self._refresh_combatants()

    def _use_skill(self, skill_name):
        if not self.combat_active or not self.enemy:
            return

        c = self.app.state.active_creature
        # BACKEND: result = self.app.backend.execute_turn(c, skill_name, self.enemy, self.environment)
        # Demo logic — reemplaza con tu motor de combate
        base_dmg = c["atk"] + random.randint(-5, 10)
        env_mod = 1.0
        if "Tormenta" in self.environment and c["type"] == "Fuego":
            env_mod = 0.7
        if "Volcánico" in self.environment and c["type"] == "Fuego":
            env_mod = 1.4
        if "Nevado" in self.environment and c["type"] == "Hielo":
            env_mod = 1.3
        dmg = max(1, int(base_dmg * env_mod))

        self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
        self._log(f"► {c['name']} usa {skill_name}!", "gold")
        self._log(f"  Daño: {dmg} (mod. ambiente: ×{env_mod:.1f})", "red")

        if self.enemy["hp"] <= 0:
            self._log(f"✓ ¡{self.enemy['name']} derrotado!", "green")
            reward = random.randint(30, 80)
            self.app.state.gold += reward
            self._log(f"  Recompensa: +{reward}g", "gold")
            self.app.sidenav.refresh_gold(self.app.state.gold)
            self._end_combat(victory=True)
            return

        # Turno enemigo
        enemy_dmg = max(1, self.enemy["atk"] + random.randint(-3, 8))
        c["hp"] = max(0, c["hp"] - enemy_dmg)
        self._log(f"◄ {self.enemy['name']} contraataca: {enemy_dmg} daño", "red")

        if c["hp"] <= 0:
            self._log(f"✗ {c['name']} ha sido derrotado...", "dim")
            self._end_combat(victory=False)
            return

        self._refresh_combatants()

    def _flee(self):
        self._log("Has huido del combate.", "dim")
        self._end_combat(victory=None)

    def _end_combat(self, victory):
        self.combat_active = False
        self.enemy = None
        self.start_btn.config(state="normal")
        self.flee_btn.config(state="disabled")
        if victory is True:
            self._log("═" * 30, "dim")
        self._refresh_combatants()

    def _log(self, text, tag=""):
        self.log_text.config(state="normal")
        if tag:
            self.log_text.insert("end", text + "\n", tag)
        else:
            self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def refresh(self):
        self._refresh_combatants()


# ══════════════════════════════════════════════════════════════
#  PANTALLA: INVENTARIO
# ══════════════════════════════════════════════════════════════
class InventoryScreen(tk.Frame):
    FILTERS = ["Todos", "Consumible", "Runa", "Accesorio", "Material"]

    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self.filter_var = tk.StringVar(value="Todos")
        self._selected_item = None
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg_panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="  🎒  INVENTARIO",
                 font=FONTS["subtitle"], fg=C["gold"],
                 bg=C["bg_panel"]).pack(side="left", pady=12, padx=8)

        # Filtros
        filt_frame = tk.Frame(hdr, bg=C["bg_panel"])
        filt_frame.pack(side="right", padx=12, pady=10)
        for f in self.FILTERS:
            rb = tk.Radiobutton(
                filt_frame, text=f, variable=self.filter_var, value=f,
                command=self._refresh,
                bg=C["bg_panel"], fg=C["text_mid"],
                selectcolor=C["bg_card"], activebackground=C["bg_panel"],
                activeforeground=C["gold"], font=FONTS["body_sm"],
                indicatoron=False, relief="flat", bd=0,
                padx=8, pady=4, cursor="hand2",
            )
            rb.pack(side="left", padx=2)

        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Grilla de ítems
        grid_outer = tk.Frame(body, bg=C["bg_panel"],
                               highlightbackground=C["border"], highlightthickness=1)
        grid_outer.pack(side="left", fill="both", expand=True, padx=(0, 8))

        canvas = tk.Canvas(grid_outer, bg=C["bg_panel"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(grid_outer, orient="vertical",
                                   command=canvas.yview)
        self.grid_frame = tk.Frame(canvas, bg=C["bg_panel"])

        self.grid_frame.bind("<Configure>",
                              lambda e: canvas.configure(
                                  scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Panel detalle
        self.detail_panel = tk.Frame(body, bg=C["bg_panel"],
                                      highlightbackground=C["border"],
                                      highlightthickness=1, width=240)
        self.detail_panel.pack(side="left", fill="y")
        self.detail_panel.pack_propagate(False)
        tk.Label(self.detail_panel, text="Selecciona un ítem",
                 font=FONTS["lore"], fg=C["text_dim"],
                 bg=C["bg_panel"]).pack(pady=40)

        self._refresh()

    def _refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        filt = self.filter_var.get()
        items = [i for i in self.app.state.inventory
                 if filt == "Todos" or i["type"] == filt]

        cols = 3
        for idx, item in enumerate(items):
            row, col = divmod(idx, cols)
            self._make_item_card(item, row, col)

        if not items:
            tk.Label(self.grid_frame, text="Sin ítems en esta categoría.",
                     font=FONTS["lore"], fg=C["text_dim"],
                     bg=C["bg_panel"]).grid(row=0, column=0, padx=20, pady=20)

    def _make_item_card(self, item, row, col):
        bg = C["bg_card"]
        card = tk.Frame(self.grid_frame, bg=bg, cursor="hand2",
                         highlightbackground=C["border"], highlightthickness=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew",
                  ipadx=8, ipady=8)

        tk.Label(card, text=item["icon"], font=("", 28),
                 bg=bg).pack()
        tk.Label(card, text=item["name"], font=FONTS["heading"],
                 fg=C["text_bright"], bg=bg, wraplength=100,
                 justify="center").pack()
        tk.Label(card, text=f"×{item['qty']}", font=FONTS["big_num"],
                 fg=C["gold"], bg=bg).pack()
        tk.Label(card, text=item["type"], font=FONTS["body_sm"],
                 fg=C["text_dim"], bg=bg).pack()

        for w in card.winfo_children() + [card]:
            w.bind("<Button-1>", lambda _, i=item: self._show_detail(i))

    def _show_detail(self, item):
        for w in self.detail_panel.winfo_children():
            w.destroy()
        bg = C["bg_panel"]

        tk.Label(self.detail_panel, text=item["icon"], font=("", 48),
                 bg=bg).pack(pady=(20, 4))
        tk.Label(self.detail_panel, text=item["name"], font=FONTS["heading"],
                 fg=C["text_bright"], bg=bg).pack()
        tk.Label(self.detail_panel, text=item["type"], font=FONTS["body_sm"],
                 fg=C["text_dim"], bg=bg).pack()
        SeparatorLine(self.detail_panel).pack(fill="x", padx=16, pady=10)
        tk.Label(self.detail_panel, text=item["desc"], font=FONTS["lore"],
                 fg=C["text_mid"], bg=bg, wraplength=200, justify="center").pack()
        SeparatorLine(self.detail_panel).pack(fill="x", padx=16, pady=10)
        tk.Label(self.detail_panel, text=f"Cantidad: {item['qty']}",
                 font=FONTS["body"], fg=C["gold"], bg=bg).pack()
        tk.Label(self.detail_panel, text=f"Valor: {item['price']}g",
                 font=FONTS["body_sm"], fg=C["text_mid"], bg=bg).pack()

        use_btn = tk.Button(
            self.detail_panel, text="✦ USAR ÍTEM",
            command=lambda: self._use_item(item),
            bg=C["green"], fg="white",
            activebackground=C["green_light"], activeforeground="white",
            font=FONTS["btn"], relief="flat", bd=0, pady=10, cursor="hand2",
        )
        use_btn.pack(fill="x", padx=20, pady=(16, 4))

        discard_btn = tk.Button(
            self.detail_panel, text="🗑 Descartar",
            command=lambda: self._discard_item(item),
            bg=C["bg_card"], fg=C["text_dim"],
            activebackground=C["bg_hover"], activeforeground=C["red_light"],
            font=FONTS["btn_sm"], relief="flat", bd=0, pady=6, cursor="hand2",
        )
        discard_btn.pack(fill="x", padx=20)

    def _use_item(self, item):
        if item["qty"] <= 0:
            messagebox.showwarning("Sin existencias", "No tienes más de este ítem.")
            return
        # BACKEND: self.app.backend.use_item(item, self.app.state.active_creature)
        item["qty"] -= 1
        messagebox.showinfo("Ítem usado",
                             f"Usaste {item['name']}.\n(Conecta tu backend para aplicar el efecto)")
        self._refresh()

    def _discard_item(self, item):
        if messagebox.askyesno("Descartar", f"¿Descartar {item['name']}?"):
            # BACKEND: self.app.backend.discard_item(item)
            self.app.state.inventory.remove(item)
            for w in self.detail_panel.winfo_children():
                w.destroy()
            tk.Label(self.detail_panel, text="Selecciona un ítem",
                     font=FONTS["lore"], fg=C["text_dim"],
                     bg=C["bg_panel"]).pack(pady=40)
            self._refresh()

    def refresh(self):
        self._refresh()


# ══════════════════════════════════════════════════════════════
#  PANTALLA: TIENDA / COMERCIO
# ══════════════════════════════════════════════════════════════
class ShopScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["bg_panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="  🏪  MERCADO OSCURO",
                 font=FONTS["subtitle"], fg=C["gold"],
                 bg=C["bg_panel"]).pack(side="left", pady=12, padx=8)

        self.gold_label = tk.Label(hdr,
                                    text=f"💰 {self.app.state.gold}g",
                                    font=FONTS["heading"], fg=C["gold"],
                                    bg=C["bg_panel"])
        self.gold_label.pack(side="right", padx=16)

        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Lista de tienda
        shop_panel = tk.Frame(body, bg=C["bg_panel"],
                               highlightbackground=C["border"], highlightthickness=1)
        shop_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(shop_panel, text="ARTÍCULOS DISPONIBLES",
                 font=FONTS["btn_sm"], fg=C["text_dim"],
                 bg=C["bg_panel"]).pack(pady=8)

        self.shop_list = tk.Frame(shop_panel, bg=C["bg_panel"])
        self.shop_list.pack(fill="both", expand=True, padx=8)

        for item in GameState.SHOP_ITEMS:
            self._make_shop_row(item)

        # Carrito / detalle
        right = tk.Frame(body, bg=C["bg_panel"],
                          highlightbackground=C["border"], highlightthickness=1,
                          width=260)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="🛒 CARRITO", font=FONTS["heading"],
                 fg=C["gold"], bg=C["bg_panel"]).pack(pady=12)
        SeparatorLine(right).pack(fill="x", padx=12)

        self.cart_frame = tk.Frame(right, bg=C["bg_panel"])
        self.cart_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.cart = {}  # {item_name: qty}

        tk.Label(right, text="Total:", font=FONTS["body"],
                 fg=C["text_mid"], bg=C["bg_panel"]).pack()
        self.total_label = tk.Label(right, text="0g", font=FONTS["big_num"],
                                     fg=C["gold"], bg=C["bg_panel"])
        self.total_label.pack()

        SeparatorLine(right).pack(fill="x", padx=12, pady=8)

        buy_btn = tk.Button(
            right, text="⚔ CONFIRMAR COMPRA",
            command=self._checkout,
            bg=C["border_gold"], fg=C["bg_dark"],
            activebackground=C["gold"], activeforeground=C["bg_dark"],
            font=FONTS["btn"], relief="flat", bd=0, pady=12, cursor="hand2",
        )
        buy_btn.pack(fill="x", padx=16, pady=(0, 12))

    def _make_shop_row(self, item):
        bg = C["bg_card"]
        row = tk.Frame(self.shop_list, bg=bg,
                        highlightbackground=C["border"], highlightthickness=1)
        row.pack(fill="x", pady=3)

        tk.Label(row, text=item["icon"], font=("", 20),
                 bg=bg).pack(side="left", padx=8, pady=6)

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True, pady=4)
        tk.Label(info, text=item["name"], font=FONTS["heading"],
                 fg=C["text_bright"], bg=bg, anchor="w").pack(fill="x")
        tk.Label(info, text=item["desc"], font=FONTS["lore"],
                 fg=C["text_dim"], bg=bg, anchor="w").pack(fill="x")

        tk.Label(row, text=f"{item['price']}g", font=FONTS["stat"],
                 fg=C["gold"], bg=bg).pack(side="right", padx=8)

        add_btn = tk.Button(
            row, text="+",
            command=lambda i=item: self._add_to_cart(i),
            bg=C["green"], fg="white",
            activebackground=C["green_light"], activeforeground="white",
            font=FONTS["btn"], relief="flat", bd=0,
            padx=10, cursor="hand2",
        )
        add_btn.pack(side="right", padx=4, pady=6)

    def _add_to_cart(self, item):
        name = item["name"]
        if name not in self.cart:
            self.cart[name] = {"item": item, "qty": 0}
        self.cart[name]["qty"] += 1
        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()
        total = 0
        for name, entry in list(self.cart.items()):
            if entry["qty"] == 0:
                continue
            subtotal = entry["item"]["price"] * entry["qty"]
            total += subtotal
            row = tk.Frame(self.cart_frame, bg=C["bg_panel"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{entry['item']['icon']} {name}",
                     font=FONTS["body_sm"], fg=C["text_bright"],
                     bg=C["bg_panel"], anchor="w").pack(side="left")
            ctrl = tk.Frame(row, bg=C["bg_panel"])
            ctrl.pack(side="right")
            tk.Button(ctrl, text="-",
                       command=lambda n=name: self._remove_from_cart(n),
                       bg=C["red"], fg="white", font=FONTS["btn_sm"],
                       relief="flat", bd=0, padx=4,
                       cursor="hand2").pack(side="left")
            tk.Label(ctrl, text=f"×{entry['qty']}",
                     font=FONTS["body_sm"], fg=C["gold"],
                     bg=C["bg_panel"], width=3).pack(side="left")
            tk.Label(ctrl, text=f"{subtotal}g",
                     font=FONTS["body_sm"], fg=C["text_mid"],
                     bg=C["bg_panel"]).pack(side="left", padx=4)

        self.total_label.config(text=f"{total}g")

    def _remove_from_cart(self, name):
        if name in self.cart and self.cart[name]["qty"] > 0:
            self.cart[name]["qty"] -= 1
        self._refresh_cart()

    def _checkout(self):
        total = sum(e["item"]["price"] * e["qty"]
                    for e in self.cart.values() if e["qty"] > 0)
        if total == 0:
            messagebox.showinfo("Carrito vacío", "Agrega ítems al carrito.")
            return
        if self.app.state.gold < total:
            messagebox.showwarning("Oro insuficiente",
                                    f"Necesitas {total}g pero tienes "
                                    f"{self.app.state.gold}g.")
            return

        # BACKEND: self.app.backend.purchase(self.cart)
        self.app.state.gold -= total
        for entry in self.cart.values():
            if entry["qty"] == 0:
                continue
            item_data = entry["item"]
            # Añadir a inventario
            existing = next(
                (i for i in self.app.state.inventory
                 if i["name"] == item_data["name"]), None)
            if existing:
                existing["qty"] += entry["qty"]
            else:
                self.app.state.inventory.append({
                    **item_data, "qty": entry["qty"]
                })

        self.cart.clear()
        self._refresh_cart()
        self.gold_label.config(text=f"💰 {self.app.state.gold}g")
        self.app.sidenav.refresh_gold(self.app.state.gold)
        messagebox.showinfo("Compra exitosa", f"Compra realizada. -{total}g")

    def refresh(self):
        self.gold_label.config(text=f"💰 {self.app.state.gold}g")


# ══════════════════════════════════════════════════════════════
#  PANTALLA PRINCIPAL (contenedor con sidenav)
# ══════════════════════════════════════════════════════════════
class MainScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg_dark"])
        self.app = app
        self._screens = {}
        self._active_key = None
        self._build()

    def _build(self):
        self.app.sidenav = SideNav(self, self.app)
        self.app.sidenav.pack(side="left", fill="y")
        self.app.sidenav.refresh_gold(self.app.state.gold)

        tk.Frame(self, bg=C["border"], width=1).pack(side="left", fill="y")

        self.content = tk.Frame(self, bg=C["bg_dark"])
        self.content.pack(side="left", fill="both", expand=True)

        self._screens = {
            "creatures": CreaturesScreen(self.content, self.app),
            "combat":    CombatScreen(self.content, self.app),
            "inventory": InventoryScreen(self.content, self.app),
            "shop":      ShopScreen(self.content, self.app),
        }

        for s in self._screens.values():
            s.place(relwidth=1, relheight=1)

        self.show("creatures")

    def show(self, key):
        if self._active_key == key:
            return
        if self._active_key and self._active_key in self._screens:
            self._screens[self._active_key].place_forget()
        self._screens[key].place(relwidth=1, relheight=1)
        if hasattr(self._screens[key], "refresh"):
            self._screens[key].refresh()
        self._active_key = key
        self.app.sidenav.set_active(key)


# ══════════════════════════════════════════════════════════════
#  CONTROLADOR PRINCIPAL
# ══════════════════════════════════════════════════════════════
class RPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chronicle of Shadows — RPG Engine")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg_dark"])
        self._style_ttk()

        self.state = GameState()
        self.sidenav = None  # Se asigna en MainScreen

        self._screens = {}
        self._active = None

        # Construir pantallas de nivel raíz
        self._screens["start"] = StartScreen(self.root, self)
        self._screens["main"]  = MainScreen(self.root, self)

        for s in self._screens.values():
            s.place(relwidth=1, relheight=1)

        self.show_screen("start")

    def _style_ttk(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=C["bg_card"],
                         background=C["bg_card"],
                         foreground=C["text_bright"],
                         selectbackground=C["bg_hover"],
                         selectforeground=C["gold"],
                         bordercolor=C["border"],
                         arrowcolor=C["gold"])
        style.configure("Vertical.TScrollbar",
                         background=C["bg_card"],
                         troughcolor=C["bg_dark"],
                         bordercolor=C["border"],
                         arrowcolor=C["text_dim"])

    def show_screen(self, key):
        if self._active:
            self._screens[self._active].place_forget()
        self._screens[key].place(relwidth=1, relheight=1)
        self._active = key

        if key == "main" and hasattr(self._screens["main"], "_screens"):
            self._screens["main"].show("creatures")

    def run(self):
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = RPGApp(root)
    app.run()