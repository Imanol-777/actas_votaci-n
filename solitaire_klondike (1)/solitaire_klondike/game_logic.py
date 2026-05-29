"""
game_logic.py
=============
Toda la lógica del juego Klondike Solitaire, completamente desacoplada de la UI.

Clases:
  - Card      : representa una carta individual.
  - Deck      : baraja de 52 cartas.
  - GameState : estado completo de la partida (stock, waste, foundations, tableau).
"""

import random
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────
# Constantes de dominio
# ──────────────────────────────────────────────────────────────
SUITS   = ["♠", "♥", "♦", "♣"]          # espadas, corazones, diamantes, tréboles
RANKS   = ["A", "2", "3", "4", "5", "6",
           "7", "8", "9", "10", "J", "Q", "K"]
RANK_VALUE = {r: i for i, r in enumerate(RANKS)}  # A=0 … K=12

# Palos rojos vs negros para validar alternancia de colores
RED_SUITS   = {"♥", "♦"}
BLACK_SUITS = {"♠", "♣"}


# ──────────────────────────────────────────────────────────────
# Carta
# ──────────────────────────────────────────────────────────────
@dataclass
class Card:
    """Representa una carta de la baraja."""
    suit: str          # uno de SUITS
    rank: str          # uno de RANKS
    face_up: bool = False

    # ── Propiedades de conveniencia ──────────────────────────
    @property
    def value(self) -> int:
        return RANK_VALUE[self.rank]

    @property
    def is_red(self) -> bool:
        return self.suit in RED_SUITS

    @property
    def is_black(self) -> bool:
        return self.suit in BLACK_SUITS

    @property
    def color(self) -> str:
        return "red" if self.is_red else "black"

    def __repr__(self) -> str:
        face = f"{self.rank}{self.suit}" if self.face_up else "??"
        return face

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


# ──────────────────────────────────────────────────────────────
# Baraja
# ──────────────────────────────────────────────────────────────
class Deck:
    """Genera y baraja las 52 cartas."""

    def __init__(self) -> None:
        self.cards: list[Card] = [
            Card(suit, rank) for suit in SUITS for rank in RANKS
        ]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self) -> Card:
        """Extrae y retorna la carta del tope."""
        return self.cards.pop()


# ──────────────────────────────────────────────────────────────
# Estado del juego
# ──────────────────────────────────────────────────────────────
class GameState:
    """
    Mantiene el estado completo de una partida Klondike.

    Zonas:
      stock      : pila de robo (cartas boca abajo).
      waste      : pila de descarte (carta superior boca arriba).
      foundations: lista de 4 pilas de fundación (A→K por palo).
      tableau    : lista de 7 columnas de juego.
    """

    def __init__(self) -> None:
        self.stock:       list[Card]        = []
        self.waste:       list[Card]        = []
        self.foundations: list[list[Card]]  = [[] for _ in range(4)]
        self.tableau:     list[list[Card]]  = [[] for _ in range(7)]
        self._deal_initial()

    # ── Repartir cartas iniciales ───────────────────────────
    def _deal_initial(self) -> None:
        deck = Deck()
        deck.shuffle()

        # Tableau: columna i recibe i+1 cartas; la última boca arriba
        for col in range(7):
            for row in range(col + 1):
                card = deck.deal()
                card.face_up = (row == col)
                self.tableau[col].append(card)

        # Resto al stock, todas boca abajo
        self.stock = deck.cards[:]
        for c in self.stock:
            c.face_up = False

    # ── Operación: robar del stock ──────────────────────────
    def draw_from_stock(self) -> bool:
        """
        Mueve la carta del tope del stock al waste (boca arriba).
        Si el stock está vacío, recicla el waste de vuelta al stock.
        Retorna True si hubo cambio.
        """
        if self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.waste.append(card)
            return True

        if self.waste:
            # Reciclar: voltear el waste de vuelta al stock
            for card in reversed(self.waste):
                card.face_up = False
                self.stock.append(card)
            self.waste.clear()
            return True

        return False

    # ── Validaciones de movimiento ──────────────────────────
    def can_place_on_tableau(self, card: Card, column: list[Card]) -> bool:
        """
        Reglas del tableau:
          - Columna vacía → solo acepta Rey (K).
          - Columna con cartas → la carta debe ser de color contrario
            y valor consecutivo menor (rank_value = top.value - 1).
        """
        if not column:
            return card.rank == "K"
        top = column[-1]
        if not top.face_up:
            return False
        return (card.color != top.color) and (card.value == top.value - 1)

    def can_place_on_foundation(self, card: Card, foundation: list[Card]) -> bool:
        """
        Reglas de fundación:
          - Vacía → solo acepta As (A).
          - Con cartas → mismo palo, valor consecutivo mayor.
        """
        if not foundation:
            return card.rank == "A"
        top = foundation[-1]
        return (card.suit == top.suit) and (card.value == top.value + 1)

    # ── Movimiento: waste → tableau/foundation ──────────────
    def move_waste_to_tableau(self, col_idx: int) -> bool:
        if not self.waste:
            return False
        card = self.waste[-1]
        col  = self.tableau[col_idx]
        if self.can_place_on_tableau(card, col):
            col.append(self.waste.pop())
            return True
        return False

    def move_waste_to_foundation(self, found_idx: int) -> bool:
        if not self.waste:
            return False
        card  = self.waste[-1]
        found = self.foundations[found_idx]
        if self.can_place_on_foundation(card, found):
            found.append(self.waste.pop())
            return True
        return False

    # ── Movimiento: tableau → foundation ───────────────────
    def move_tableau_to_foundation(self, col_idx: int, found_idx: int) -> bool:
        col   = self.tableau[col_idx]
        found = self.foundations[found_idx]
        if not col:
            return False
        card = col[-1]
        if not card.face_up:
            return False
        if self.can_place_on_foundation(card, found):
            found.append(col.pop())
            self._flip_top(col)
            return True
        return False

    # ── Movimiento: tableau → tableau (una o varias cartas) ─
    def move_tableau_to_tableau(
        self,
        src_col: int,
        card_idx: int,
        dst_col: int
    ) -> bool:
        """
        Mueve las cartas desde card_idx hasta el final de src_col a dst_col.
        card_idx es el índice dentro de la columna origen.
        """
        src  = self.tableau[src_col]
        dst  = self.tableau[dst_col]
        pile = src[card_idx:]           # sub-pila a mover

        if not pile or not pile[0].face_up:
            return False
        if self.can_place_on_tableau(pile[0], dst):
            dst.extend(pile)
            del src[card_idx:]
            self._flip_top(src)
            return True
        return False

    # ── Movimiento: foundation → tableau ───────────────────
    def move_foundation_to_tableau(self, found_idx: int, col_idx: int) -> bool:
        found = self.foundations[found_idx]
        col   = self.tableau[col_idx]
        if not found:
            return False
        card = found[-1]
        if self.can_place_on_tableau(card, col):
            col.append(found.pop())
            return True
        return False

    # ── Voltear carta superior boca arriba ──────────────────
    def _flip_top(self, column: list[Card]) -> None:
        if column and not column[-1].face_up:
            column[-1].face_up = True

    # ── Condición de victoria ────────────────────────────────
    @property
    def is_won(self) -> bool:
        """La partida está ganada cuando las 4 fundaciones tienen 13 cartas."""
        return all(len(f) == 13 for f in self.foundations)

    # ── Auto-completar (move carta a fundación automáticamente) ──
    def auto_move_to_foundation(self) -> bool:
        """
        Intenta mover una carta de tableau o waste a cualquier fundación.
        Retorna True si logró al menos un movimiento.
        """
        moved = False

        # Desde waste
        for fi in range(4):
            if self.move_waste_to_foundation(fi):
                moved = True
                break

        # Desde cada columna del tableau
        for ci in range(7):
            for fi in range(4):
                if self.move_tableau_to_foundation(ci, fi):
                    moved = True
                    break

        return moved
