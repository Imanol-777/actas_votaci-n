"""
card_widget.py
==============
Widget visual para una carta individual del Klondike Solitaire.
Compatible con Flet 0.85.x (API nueva: Border, Padding explícitos).

Responsabilidades:
  - Renderizar la cara o el reverso de la carta.
  - Exponer un ft.Draggable cuando la carta está boca arriba.
  - Estilo "tapete de casino": verde oscuro, cartas con sombra.
"""

import flet as ft
from game_logic import Card


# ──────────────────────────────────────────────────────────────
# Dimensiones y colores globales
# ──────────────────────────────────────────────────────────────
CARD_W          = 72
CARD_H          = 100
CARD_RADIUS     = 6
CARD_BG         = "#FAFAFA"
CARD_BACK_BG    = "#1A237E"
CARD_BACK_INNER = "#283593"
COLOR_RED       = "#C62828"
COLOR_BLACK     = "#212121"
EMPTY_SLOT_BDR  = "#FFFFFF"   # se usa con opacity

CARD_SHADOW = ft.BoxShadow(
    spread_radius=1,
    blur_radius=4,
    color=ft.Colors.with_opacity(0.4, "#000000"),
    offset=ft.Offset(1, 2),
)


# ──────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────
def _suit_color(suit: str) -> str:
    return COLOR_RED if suit in {"♥", "♦"} else COLOR_BLACK


def _all_border(width: float, color: str) -> ft.Border:
    """Crea un Border uniforme en los 4 lados (reemplaza border.all)."""
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, bottom=side, left=side, right=side)


def _pad(v: float) -> ft.Padding:
    """Crea un Padding uniforme (reemplaza padding.all)."""
    return ft.Padding(left=v, top=v, right=v, bottom=v)


def _pad_sym(h: float, v: float) -> ft.Padding:
    return ft.Padding(left=h, right=h, top=v, bottom=v)


# ──────────────────────────────────────────────────────────────
# Cara de la carta (boca arriba)
# ──────────────────────────────────────────────────────────────
def _card_face(card: Card) -> ft.Container:
    color = _suit_color(card.suit)

    top_left = ft.Column(
        controls=[
            ft.Text(card.rank, size=13, weight=ft.FontWeight.BOLD,
                    color=color, height=15),
            ft.Text(card.suit, size=11, color=color, height=13),
        ],
        spacing=0,
        tight=True,
    )

    center = ft.Text(
        card.suit,
        size=30,
        color=color,
        text_align=ft.TextAlign.CENTER,
    )

    # Esquina inferior derecha: girado 180° usando RotatedBox(quarter_turns=2)
    bottom_right = ft.RotatedBox(
        quarter_turns=2,
        content=ft.Column(
            controls=[
                ft.Text(card.rank, size=13, weight=ft.FontWeight.BOLD,
                        color=color, height=15),
                ft.Text(card.suit, size=11, color=color, height=13),
            ],
            spacing=0,
            tight=True,
        ),
    )

    return ft.Container(
        width=CARD_W,
        height=CARD_H,
        bgcolor=CARD_BG,
        border_radius=CARD_RADIUS,
        border=_all_border(1, ft.Colors.with_opacity(0.3, "#000000")),
        shadow=CARD_SHADOW,
        padding=_pad(4),
        content=ft.Stack(
            controls=[
                ft.Container(content=top_left,   top=3,    left=4),
                ft.Container(
                    content=center,
                    top=0, left=0, right=0, bottom=0,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(content=bottom_right, bottom=3, right=4),
            ]
        ),
    )


# ──────────────────────────────────────────────────────────────
# Reverso de la carta (boca abajo)
# ──────────────────────────────────────────────────────────────
def _card_back() -> ft.Container:
    return ft.Container(
        width=CARD_W,
        height=CARD_H,
        bgcolor=CARD_BACK_BG,
        border_radius=CARD_RADIUS,
        border=_all_border(1, ft.Colors.with_opacity(0.3, "#000000")),
        shadow=CARD_SHADOW,
        padding=_pad(5),
        content=ft.Container(
            border_radius=4,
            bgcolor=CARD_BACK_INNER,
            border=_all_border(2, ft.Colors.with_opacity(0.5, "#FFFFFF")),
            expand=True,
            content=ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "🂠", size=28,
                    color=ft.Colors.with_opacity(0.3, "#FFFFFF"),
                ),
            ),
        ),
    )


# ──────────────────────────────────────────────────────────────
# Casilla vacía (placeholder de columna / fundación)
# ──────────────────────────────────────────────────────────────
def empty_slot(label: str = "") -> ft.Container:
    return ft.Container(
        width=CARD_W,
        height=CARD_H,
        border_radius=CARD_RADIUS,
        border=_all_border(2, ft.Colors.with_opacity(0.25, EMPTY_SLOT_BDR)),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            label, size=20,
            color=ft.Colors.with_opacity(0.5, "#FFFFFF"),
        ),
    )


# ──────────────────────────────────────────────────────────────
# Widget completo: draggable card
# ──────────────────────────────────────────────────────────────
def make_card_widget(
    card: Card,
    drag_group: str,
    drag_data: str,
    draggable: bool = True,
) -> ft.Control:
    """
    Retorna el control final para una carta.

    - Boca abajo  → solo reverso (no draggable).
    - Boca arriba → ft.Draggable con cara visible si draggable=True,
                    solo la cara si draggable=False.

    Parámetros
    ----------
    card        : la carta a renderizar.
    drag_group  : grupo compartido con los DragTarget destino.
    drag_data   : JSON string con info del origen del arrastre.
    draggable   : False desactiva el arrastre (p.ej. cartas intermedias).
    """
    visual = _card_face(card) if card.face_up else _card_back()

    if not card.face_up or not draggable:
        return visual

    return ft.Draggable(
        group=drag_group,
        data=drag_data,
        content=visual,
        content_feedback=ft.Container(opacity=0.75, content=_card_face(card)),
    )
