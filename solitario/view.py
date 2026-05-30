import tkinter as tk
from tkinter import filedialog, messagebox

from cartas import Carta, SUITS, SUIT_SYMBOL, SUIT_NAME_ES
from config import (
    CARD_W, CARD_H, COL_BLUE, MARGIN, TOP_Y, TABLEAU_Y, FD_OFF, FU_OFF,
    CANVAS_W, CANVAS_H, COL_FELT, COL_CARD, COL_BACK, COL_BACK2,
    COL_SLOT, COL_SLOT_LINE, COL_RED, COL_BLACK, COL_GOLD, col_x,
)
from game import Solitario
from image_rey import make_photo, HAS_PIL


class SolitarioUI:
    def __init__(self, root):
        self.root = root
        self.game = Solitario()

        self.root.title("Solitario ♠ ♥ ♦ ♣")
        self.root.configure(bg=COL_FELT)
        self.root.resizable(False, False)

        # Fuentes
        self.f_corner = ("Helvetica", 16, "bold")
        self.f_center = ("Helvetica", 44, "bold")
        self.f_face = ("Helvetica", 40, "bold")
        self.f_small = ("Helvetica", 11)

        # Imágenes personalizadas de los reyes: palo -> PhotoImage
        self.king_images = {}

        # Imágenes personalizadas de los ases: palo -> PhotoImage
        self.ace_images = {}

        # Estado del arrastre y registro de dibujo para detectar clics
        self.drag = None
        self.draw_order = []

        self._build_menu()

        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H,
                                bg=COL_FELT, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(root, text="", bg=COL_FELT, fg="white",
                               font=self.f_small, anchor="w")
        self.status.pack(fill="x", padx=MARGIN, pady=(0, 6))

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double)

        self.redraw()

    # Menu
    def _build_menu(self):
        menubar = tk.Menu(self.root)

        m_game = tk.Menu(menubar, tearoff=0)
        m_game.add_command(label="Nueva partida", command=self.new_game, accelerator="F2")
        m_game.add_separator()
        m_game.add_command(label="Cómo jugar", command=self.show_help)
        m_game.add_separator()
        m_game.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Juego", menu=m_game)

        m_king = tk.Menu(menubar, tearoff=0)
        for s in SUITS:
            m_king.add_command(
                label="Cargar imagen → Rey de %s %s" % (SUIT_NAME_ES[s], SUIT_SYMBOL[s]),
                command=lambda su=s: self.load_king_image(su),
            )
        m_king.add_separator()
        m_king.add_command(label="Restablecer reyes", command=self.reset_kings)
        menubar.add_cascade(label="Reyes", menu=m_king)

        self.root.config(menu=menubar)
        self.root.bind("<F2>", lambda e: self.new_game())

        m_ace = tk.Menu(menubar, tearoff=0)
        for s in SUITS:
            m_ace.add_command(
                label="Cargar imagen → As de %s %s" % (SUIT_NAME_ES[s], SUIT_SYMBOL[s]),
                command=lambda su=s: self.load_ace_image(su),
            )
        m_ace.add_separator()
        m_ace.add_command(label="Restablecer ases", command=self.reset_aces)
        menubar.add_cascade(label="Ases", menu=m_ace)

    def show_help(self):
        messagebox.showinfo(
            "Cómo jugar",
            "Objetivo: llevar las 4 fundaciones de As a Rey, una por palo.\n\n"
            "• Arrastra y suelta cartas entre columnas (descendente y de color alterno).\n"
            "• Solo un Rey puede ir a una columna vacía.\n"
            "• Haz clic en el mazo (arriba a la izquierda) para robar una carta.\n"
            "• Si el mazo se vacía, haz clic en su hueco para reciclar.\n"
            "• Doble clic en una carta para enviarla a su fundación automáticamente.\n\n"
            "Menú “Reyes”: carga una imagen de tu dispositivo para cada rey.",
        )

    # Acciones de juego
    def new_game(self):
        self.game.new_game()
        self.drag = None
        self.redraw()

    # ================== Imágenes de reyes ==================
    def load_king_image(self, suit):
        if HAS_PIL:
            ftypes = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("Todos", "*.*")]
        else:
            ftypes = [("Imágenes PNG/GIF", "*.png *.gif"), ("Todos", "*.*")]
        path = filedialog.askopenfilename(
            title="Elige la imagen para el Rey de %s" % SUIT_NAME_ES[suit],
            filetypes=ftypes,
        )
        if not path:
            return
        try:
            photo = make_photo(path)
        except Exception as e:
            messagebox.showerror(
                "No se pudo cargar la imagen",
                "Ocurrió un error al abrir la imagen:\n%s\n\n"
                "Sugerencia: instala Pillow para admitir JPG y otros formatos:\n"
                "    pip install pillow" % e,
            )
            return
        self.king_images[suit] = photo
        self.redraw()

    def reset_kings(self):
        self.king_images.clear()
        self.redraw()
 
    # ================== Imágenes de ases ==================
    def load_ace_image(self, suit):
        if HAS_PIL:
            ftypes = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("Todos", "*.*")]
        else:
            ftypes = [("Imágenes PNG/GIF", "*.png *.gif"), ("Todos", "*.*")]
        path = filedialog.askopenfilename(
            title="Elige la imagen para el As de %s" % SUIT_NAME_ES[suit],
            filetypes=ftypes,
        )
        if not path:
            return
        try:
            photo = make_photo(path)
        except Exception as e:
            messagebox.showerror(
                "No se pudo cargar la imagen",
                "Ocurrió un error al abrir la imagen:\n%s\n\n"
                "Sugerencia: instala Pillow para admitir JPG y otros formatos:\n"
                "    pip install pillow" % e,
            )
            return
        self.ace_images[suit] = photo
        self.redraw()

    def reset_aces(self):
        self.ace_images.clear()
        self.redraw()

    # ================== Dibujo ==================
    def round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(pts, smooth=True, **kw)

    def draw_slot(self, x, y, glyph=""):
        self.round_rect(x, y, x + CARD_W, y + CARD_H, 10,
                        fill=COL_SLOT, outline=COL_SLOT_LINE, width=2)
        if glyph:
            self.canvas.create_text(x + CARD_W / 2, y + CARD_H / 2,
                                    text=glyph, fill=COL_SLOT_LINE,
                                    font=("Helvetica", 30, "bold"))

    def draw_card(self, card, x, y):
        if not card.face_up:
            self.round_rect(x, y, x + CARD_W, y + CARD_H, 10,
                            fill=COL_BACK, outline="#0c1c4a", width=2)
            self.round_rect(x + 8, y + 8, x + CARD_W - 8, y + CARD_H - 8, 7,
                            fill=COL_BACK2, outline=COL_BACK)
            self.canvas.create_text(x + CARD_W / 2, y + CARD_H / 2,
                                    text="♣♠", fill=COL_BACK,
                                    font=("Helvetica", 22, "bold"))
            return
        
        fill = COL_RED if card.color == "red" else COL_BLACK
        king_custom = card.rank == 13 and card.suit in self.king_images
        ace_custom  = card.rank == 1  and card.suit in self.ace_images
        if king_custom:
            outline, width = COL_GOLD, 3
        elif ace_custom:
            outline, width = COL_BLUE, 3
        else:
            outline, width = "#c9c9bd", 1
        self.round_rect(x, y, x + CARD_W, y + CARD_H, 10,
                        fill=COL_CARD, outline=outline, width=width)

        # Índices en las esquinas
        self.canvas.create_text(x + 8, y + 6, text=card.label, fill=fill,
                                 font=self.f_corner, anchor="nw")
        self.canvas.create_text(x + 9, y + 27, text=card.symbol, fill=fill,
                                 font=("Helvetica", 14), anchor="nw")
        self.canvas.create_text(x + CARD_W - 8, y + CARD_H - 6, text=card.label,
                                 fill=fill, font=self.f_corner, anchor="se")
        self.canvas.create_text(x + CARD_W - 9, y + CARD_H - 27, text=card.symbol,
                                 fill=fill, font=("Helvetica", 14), anchor="se")

        cx, cy = x + CARD_W / 2, y + CARD_H / 2 + 4
        if king_custom:
            self.canvas.create_image(cx, cy, image=self.king_images[card.suit])
        elif ace_custom:
            self.canvas.create_image(cx, cy, image=self.ace_images[card.suit])
        elif card.rank in (11, 12, 13):
            self.canvas.create_text(cx, cy, text=card.label, fill=fill, font=self.f_face)
        else:
            self.canvas.create_text(cx, cy, text=card.symbol, fill=fill, font=self.f_center)

    def _column_layout(self, cards):
        """Lista de coordenadas Y para cada carta visible, comprimiendo si no cabe."""
        n = len(cards)
        if n == 0:
            return []
        gaps = [FD_OFF if not cards[k].face_up else FU_OFF for k in range(n - 1)]
        span = sum(gaps)
        available = CANVAS_H - MARGIN - CARD_H - TABLEAU_Y
        if span > available and span > 0:
            scale = available / span
            gaps = [g * scale for g in gaps]
        ys = [TABLEAU_Y]
        for g in gaps:
            ys.append(ys[-1] + g)
        return ys

    def redraw(self):
        g = self.game
        c = self.canvas
        c.delete("all")
        self.draw_order = []
        dragging = set(id(x) for x in self.drag["cards"]) if self.drag else set()

        # Mazo (stock)
        sx = col_x(0)
        if g.stock:
            self.draw_card(Carta(0, "spades"), sx, TOP_Y)   # dorso genérico
        else:
            self.draw_slot(sx, TOP_Y, "↺")

        # Descarte (waste)
        wx = col_x(1)
        self.draw_slot(wx, TOP_Y)
        top_waste = next((cd for cd in reversed(g.waste) if id(cd) not in dragging), None)
        if top_waste is not None:
            self.draw_card(top_waste, wx, TOP_Y)
            self.draw_order.append((top_waste, wx, TOP_Y))

        # Fundaciones
        for k in range(4):
            fx = col_x(3 + k)
            self.draw_slot(fx, TOP_Y, "A")
            top = next((cd for cd in reversed(g.foundations[k]) if id(cd) not in dragging), None)
            if top is not None:
                self.draw_card(top, fx, TOP_Y)
                self.draw_order.append((top, fx, TOP_Y))

        # Columnas (tableau)
        for i in range(7):
            x = col_x(i)
            visible = [cd for cd in g.tableau[i] if id(cd) not in dragging]
            if not visible:
                self.draw_slot(x, TABLEAU_Y)
                continue
            for cd, y in zip(visible, self._column_layout(visible)):
                self.draw_card(cd, x, y)
                self.draw_order.append((cd, x, y))

        # Cartas que se están arrastrando, por encima de todo
        if self.drag:
            dx, dy = self.drag["x"], self.drag["y"]
            for idx, cd in enumerate(self.drag["cards"]):
                self.draw_card(cd, dx, dy + idx * FU_OFF)

        self.status.config(
            text="Movimientos: %d   |   Mazo: %d   Descarte: %d   Fundaciones: %d/52"
            % (g.moves, len(g.stock), len(g.waste), sum(len(f) for f in g.foundations))
        )

    # ================== Detección con el ratón ==================
    def card_at(self, px, py):
        for card, x, y in reversed(self.draw_order):
            if x <= px <= x + CARD_W and y <= py <= y + CARD_H:
                return card, x, y
        return None

    def pile_at(self, px, py):
        for k in range(4):   # fundaciones
            fx = col_x(3 + k)
            if fx <= px <= fx + CARD_W and TOP_Y - 4 <= py <= TOP_Y + CARD_H + 4:
                return ("foundation", k)
        for i in range(7):   # columnas
            tx = col_x(i)
            if tx <= px <= tx + CARD_W and py >= TABLEAU_Y - 10:
                return ("tableau", i)
        return None

    # ================== Eventos ==================
    def on_press(self, e):
        if col_x(0) <= e.x <= col_x(0) + CARD_W and TOP_Y <= e.y <= TOP_Y + CARD_H:
            self.game.draw_stock()
            self.redraw()
            return

        hit = self.card_at(e.x, e.y)
        if not hit:
            return
        card, x, y = hit
        loc = self.game.locate(card)
        if not loc:
            return
        kind = loc[0]

        if kind == "waste":
            if self.game.waste and self.game.waste[-1] is card:
                self.start_drag([card], ("waste", 0), x, y, e)
        elif kind == "foundation":
            k = loc[1]
            if self.game.foundations[k] and self.game.foundations[k][-1] is card:
                self.start_drag([card], ("foundation", k), x, y, e)
        elif kind == "tableau":
            i, idx = loc[1], loc[2]
            if not card.face_up:
                return
            group = self.game.tableau[i][idx:]
            if self.game.is_sequence(group):
                self.start_drag(group, ("tableau", i), x, y, e)

    def start_drag(self, cards, source, x, y, e):
        self.drag = {
            "cards": cards, "source": source,
            "x": x, "y": y, "offx": e.x - x, "offy": e.y - y,
        }
        self.redraw()

    def on_motion(self, e):
        if not self.drag:
            return
        self.drag["x"] = e.x - self.drag["offx"]
        self.drag["y"] = e.y - self.drag["offy"]
        self.redraw()

    def on_release(self, e):
        if not self.drag:
            return
        cards = self.drag["cards"]
        source = self.drag["source"]
        cx = self.drag["x"] + CARD_W / 2
        cy = self.drag["y"] + CARD_H / 2
        dest = self.pile_at(cx, cy)

        moved = False
        if dest:
            dkind, didx = dest
            if dkind == "foundation" and len(cards) == 1 and self.game.can_to_foundation(cards[0], didx):
                self.game.move(cards, source, ("foundation", didx))
                moved = True
            elif dkind == "tableau" and self.game.can_to_tableau(cards[0], didx) and self.game.is_sequence(cards):
                if not (source[0] == "tableau" and source[1] == didx):
                    self.game.move(cards, source, ("tableau", didx))
                    moved = True

        self.drag = None
        self.redraw()
        if moved:
            self._check_win()

    def on_double(self, e):
        hit = self.card_at(e.x, e.y)
        if not hit:
            return
        card, _, _ = hit
        loc = self.game.locate(card)
        if not loc:
            return
        kind = loc[0]
        if kind == "waste":
            if not (self.game.waste and self.game.waste[-1] is card):
                return
            source = ("waste", 0)
        elif kind == "tableau":
            i = loc[1]
            if not (self.game.tableau[i] and self.game.tableau[i][-1] is card):
                return
            source = ("tableau", i)
        else:
            return
        for k in range(4):
            if self.game.can_to_foundation(card, k):
                self.game.move([card], source, ("foundation", k))
                self.redraw()
                self._check_win()
                return

    def _check_win(self):
        if self.game.is_won():
            if messagebox.askyesno(
                "¡Ganaste!",
                "\U0001f389 ¡Completaste el solitario en %d movimientos!\n\n"
                "¿Jugar otra partida?" % self.game.moves,
            ):
                self.new_game()
