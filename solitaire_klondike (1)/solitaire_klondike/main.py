"""
main.py
=======
Punto de entrada — Klondike Solitaire con Flet 0.85.x / Python 3.14.

Arquitectura:
  SolitaireApp  — orquesta la UI y delega la lógica a GameState.

Zonas de la pantalla:
  ┌──────────────────────────────────────────┐
  │  [Stock] [Waste]    [F♠][F♥][F♦][F♣]    │  ← fila superior
  │                                          │
  │  [T0][T1][T2][T3][T4][T5][T6]           │  ← tableau (7 columnas)
  └──────────────────────────────────────────┘
"""

import json
import flet as ft

from game_logic import GameState, SUITS
from card_widget import (
    CARD_W, CARD_H, CARD_RADIUS,
    make_card_widget, empty_slot,
    _card_back,
    _all_border, _pad, _pad_sym,
)


# ──────────────────────────────────────────────────────────────
# Constantes de UI
# ──────────────────────────────────────────────────────────────
FELT_GREEN   = "#1B5E20"
COL_SPACING  = 8
OVERLAP_DOWN = 20       # px visibles de carta boca-abajo apilada
OVERLAP_UP   = 28       # px visibles de carta boca-arriba apilada
DRAG_GROUP   = "card"


# ──────────────────────────────────────────────────────────────
# Aplicación principal
# ──────────────────────────────────────────────────────────────
class SolitaireApp:
    """
    Gestiona toda la UI y los eventos del usuario.

    Flujo:
      _build_ui() → crea contenedores de referencia
      _refresh()  → lee GameState y rellena cada contenedor
      _on_*()     → actualizan GameState y llaman _refresh()
    """

    def __init__(self, page: ft.Page) -> None:
        self.page  = page
        self.state = GameState()
        self._setup_page()
        self._build_ui()

    # ── Configurar ventana ───────────────────────────────────
    def _setup_page(self) -> None:
        p = self.page
        p.title      = "♠ Klondike Solitaire"
        p.bgcolor    = FELT_GREEN
        p.padding    = ft.Padding(left=0, top=0, right=0, bottom=0)
        p.theme_mode = ft.ThemeMode.DARK
        p.window.width      = 620
        p.window.height     = 820
        p.window.min_width  = 560
        p.window.min_height = 700
        p.window.resizable  = True

    # ── Construir árbol inicial de controles ─────────────────
    def _build_ui(self) -> None:

        # Header
        self._header = self._make_header()

        # Zona superior: stock + waste + espaciador + 4 fundaciones
        self._stock_ref  = ft.Container(width=CARD_W, height=CARD_H)
        self._waste_ref  = ft.Container(width=CARD_W, height=CARD_H)
        self._found_refs = [ft.Container(width=CARD_W, height=CARD_H)
                            for _ in range(4)]

        top_row = ft.Row(
            controls=[
                self._stock_ref,
                self._waste_ref,
                ft.Container(width=CARD_W),   # separador visual
                *self._found_refs,
            ],
            spacing=COL_SPACING,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Tableau: 7 columnas
        self._tab_refs = [ft.Container(width=CARD_W) for _ in range(7)]

        tab_row = ft.Row(
            controls=self._tab_refs,
            spacing=COL_SPACING,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Contenedor principal scrolleable
        main_col = ft.Column(
            controls=[
                self._header,
                top_row,
                ft.Container(height=10),
                tab_row,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        self.page.add(
            ft.Container(
                content=main_col,
                bgcolor=FELT_GREEN,
                expand=True,
                padding=_pad_sym(16, 12),
            )
        )

        self._refresh()

    # ── Header ───────────────────────────────────────────────
    def _make_header(self) -> ft.Row:
        btn_style = ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.2, "#FFFFFF"),
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        return ft.Row(
            controls=[
                ft.Text(
                    "♠ Klondike Solitaire",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                ft.Row(
                    controls=[
                        ft.Button(
                            "Nueva partida",
                            icon=ft.Icons.REFRESH,
                            on_click=self._on_new_game,
                            style=btn_style,
                        ),
                        ft.Button(
                            "Auto ♠",
                            icon=ft.Icons.AUTO_AWESOME,
                            on_click=self._on_auto_move,
                            style=btn_style,
                            tooltip="Mover cartas a fundaciones automáticamente",
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    # ──────────────────────────────────────────────────────────
    # REFRESH — traduce GameState → widgets
    # ──────────────────────────────────────────────────────────
    def _refresh(self) -> None:
        self._render_stock()
        self._render_waste()
        for i in range(4):
            self._render_foundation(i)
        for i in range(7):
            self._render_tableau(i)
        self.page.update()
        if self.state.is_won:
            self._show_win_dialog()

    # ── Stock ────────────────────────────────────────────────
    def _render_stock(self) -> None:
        if self.state.stock:
            inner: ft.Control = ft.GestureDetector(
                on_tap=self._on_stock_tap,
                mouse_cursor=ft.MouseCursor.CLICK,
                content=_card_back(),
            )
        elif self.state.waste:
            # Vacío pero reciclable
            inner = ft.GestureDetector(
                on_tap=self._on_stock_tap,
                mouse_cursor=ft.MouseCursor.CLICK,
                content=ft.Container(
                    width=CARD_W, height=CARD_H,
                    border_radius=CARD_RADIUS,
                    border=_all_border(2, ft.Colors.with_opacity(0.3, "#FFFFFF")),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.REFRESH_ROUNDED,
                        color=ft.Colors.with_opacity(0.7, "#FFFFFF"),
                        size=32,
                    ),
                ),
            )
        else:
            inner = empty_slot()

        self._stock_ref.content = inner

    # ── Waste ────────────────────────────────────────────────
    def _render_waste(self) -> None:
        if not self.state.waste:
            self._waste_ref.content = empty_slot()
            return

        top = self.state.waste[-1]
        drag_data = json.dumps({"src": "waste"})
        self._waste_ref.content = make_card_widget(
            top, DRAG_GROUP, drag_data, draggable=True
        )

    # ── Fundación ────────────────────────────────────────────
    def _render_foundation(self, idx: int) -> None:
        found    = self.state.foundations[idx]
        suit_lbl = SUITS[idx]

        if found:
            top       = found[-1]
            drag_data = json.dumps({"src": "foundation", "idx": idx})
            inner: ft.Control = make_card_widget(
                top, DRAG_GROUP, drag_data, draggable=True
            )
        else:
            inner = empty_slot(suit_lbl)

        target = ft.DragTarget(
            group=DRAG_GROUP,
            content=inner,
            on_accept=lambda e, i=idx: self._on_drop_foundation(e, i),
        )
        self._found_refs[idx].content = target

    # ── Columna del tableau ──────────────────────────────────
    def _render_tableau(self, col_idx: int) -> None:
        """
        Apila las cartas con offset vertical progresivo usando ft.Stack.
        Cada carta boca-arriba es Draggable. La zona de drop cubre la
        carta visible más alta (o el slot vacío si la columna está vacía).
        """
        col = self.state.tableau[col_idx]

        # ── Columna vacía ────────────────────────────────────
        if not col:
            drop_zone = ft.DragTarget(
                group=DRAG_GROUP,
                content=empty_slot("K"),
                on_accept=lambda e, c=col_idx: self._on_drop_tableau(e, c),
            )
            self._tab_refs[col_idx].content = drop_zone
            self._tab_refs[col_idx].height  = CARD_H
            return

        # ── Columna con cartas ───────────────────────────────
        stack_items: list[ft.Control] = []
        y = 0
        for i, card in enumerate(col):
            drag_data = json.dumps({"src": "tableau", "col": col_idx, "idx": i})
            widget    = make_card_widget(card, DRAG_GROUP, drag_data,
                                         draggable=card.face_up)
            stack_items.append(
                ft.Container(content=widget, top=y, left=0)
            )
            # Calcular offset para la siguiente carta
            if i < len(col) - 1:
                y += OVERLAP_UP if card.face_up else OVERLAP_DOWN

        total_h = y + CARD_H

        # Zona de drop transparente encima de la última carta
        drop_overlay = ft.DragTarget(
            group=DRAG_GROUP,
            content=ft.Container(
                width=CARD_W,
                height=CARD_H,
                bgcolor=ft.Colors.with_opacity(0, "#000000"),
            ),
            on_accept=lambda e, c=col_idx: self._on_drop_tableau(e, c),
        )
        stack_items.append(ft.Container(content=drop_overlay, top=y, left=0))

        self._tab_refs[col_idx].content = ft.Stack(
            controls=stack_items,
            width=CARD_W,
            height=total_h,
            clip_behavior=ft.ClipBehavior.NONE,
        )
        self._tab_refs[col_idx].height = total_h

    # ──────────────────────────────────────────────────────────
    # HANDLERS
    # ──────────────────────────────────────────────────────────
    def _on_stock_tap(self, e) -> None:
        self.state.draw_from_stock()
        self._refresh()

    def _on_new_game(self, e) -> None:
        self.state = GameState()
        self._refresh()

    def _on_auto_move(self, e) -> None:
        moved = True
        while moved:
            moved = self.state.auto_move_to_foundation()
        self._refresh()

    def _on_drop_foundation(self, e: ft.DragTargetEvent, found_idx: int) -> None:
        # e.data puede ser None si el drag no transportó datos válidos
        if not e.data:
            return
        try:
            data = json.loads(e.data)
        except (TypeError, ValueError):
            return

        src   = data.get("src")
        moved = False

        if src == "waste":
            moved = self.state.move_waste_to_foundation(found_idx)
        elif src == "tableau":
            moved = self.state.move_tableau_to_foundation(data["col"], found_idx)
        # foundation → foundation no permitido

        if moved:
            self._refresh()

    def _on_drop_tableau(self, e: ft.DragTargetEvent, dst_col: int) -> None:
        # e.data puede ser None si el drag no transportó datos válidos
        if not e.data:
            return
        try:
            data = json.loads(e.data)
        except (TypeError, ValueError):
            return

        src   = data.get("src")
        moved = False

        if src == "waste":
            moved = self.state.move_waste_to_tableau(dst_col)
        elif src == "tableau":
            src_col  = data["col"]
            card_idx = data["idx"]
            if src_col != dst_col:
                moved = self.state.move_tableau_to_tableau(src_col, card_idx, dst_col)
        elif src == "foundation":
            moved = self.state.move_foundation_to_tableau(data["idx"], dst_col)

        if moved:
            self._refresh()

    # ── Diálogo de victoria ──────────────────────────────────
    def _show_win_dialog(self) -> None:
        def close(_):
            dlg.open = False
            self.page.update()

        def new_game(_):
            dlg.open = False
            self.state = GameState()
            self._refresh()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🎉 ¡Ganaste!", size=24, weight=ft.FontWeight.BOLD,
                          text_align=ft.TextAlign.CENTER),
            content=ft.Text(
                "¡Completaste el Klondike Solitaire!\n¿Quieres jugar de nuevo?",
                text_align=ft.TextAlign.CENTER,
                size=16,
            ),
            actions=[
                ft.TextButton("Cerrar",              on_click=close),
                ft.Button("Nueva partida 🃏",         on_click=new_game),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


# ──────────────────────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────────────────────
def main(page: ft.Page) -> None:
    SolitaireApp(page)


if __name__ == "__main__":
    ft.run(main)
