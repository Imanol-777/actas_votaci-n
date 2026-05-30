import random

from cartas import Carta, SUITS, Carta

class Solitario:

    def __init__(self):
        self.new_game()

    # ------------------------------------------------------------------
    def new_game(self):
        deck = [Carta(r, s) for s in SUITS for r in range(1, 14)]
        random.shuffle(deck)

        self.tableau = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i, 7):
                self.tableau[j].append(deck.pop())
        for col in self.tableau:
            col[-1].face_up = True

        self.stock = deck            # resto, boca abajo
        self.waste = []
        self.foundations = [[], [], [], []]
        self.moves = 0

    # ------------------------------------------------------------------
    # Localización de una carta dentro del estado
    # ------------------------------------------------------------------
    def locate(self, card):
        for idx, cd in enumerate(self.waste):
            if cd is card:
                return ("waste", 0, idx)
        for k, f in enumerate(self.foundations):
            for idx, cd in enumerate(f):
                if cd is card:
                    return ("foundation", k, idx)
        for i, col in enumerate(self.tableau):
            for idx, cd in enumerate(col):
                if cd is card:
                    return ("tableau", i, idx)
        return None

    # Reglas

    def can_to_foundation(self, card, k):
        f = self.foundations[k]
        if not f:
            return card.rank == 1
        top = f[-1]
        return card.suit == top.suit and card.rank == top.rank + 1

    def can_to_tableau(self, card, i):
        col = self.tableau[i]
        if not col:
            return card.rank == 13
        top = col[-1]
        return top.face_up and card.color != top.color and card.rank == top.rank - 1

    @staticmethod
    def is_sequence(cards):
        """True si la lista es descendente y de color alterno, toda boca arriba."""
        if not cards:
            return False
        for a, b in zip(cards, cards[1:]):
            if not a.face_up or not b.face_up:
                return False
            if b.rank != a.rank - 1 or b.color == a.color:
                return False
        return cards[0].face_up

    # Movimientos

    def draw_stock(self):
        """Roba una carta del mazo al descarte; si el mazo está vacío, lo recicla."""
        if self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.waste.append(card)
        elif self.waste:
            while self.waste:
                card = self.waste.pop()
                card.face_up = False
                self.stock.append(card)
        self.moves += 1

    def move(self, cards, source, dest):

        skind = source[0]
        if skind == "waste":
            self.waste.pop()
        elif skind == "foundation":
            self.foundations[source[1]].pop()
        elif skind == "tableau":
            col = self.tableau[source[1]]
            del col[len(col) - len(cards):]
            if col and not col[-1].face_up:
                col[-1].face_up = True  # descubrir la carta que queda arriba

        dkind = dest[0]
        if dkind == "foundation":
            self.foundations[dest[1]].append(cards[0])
        elif dkind == "tableau":
            self.tableau[dest[1]].extend(cards)

        self.moves += 1

    def is_won(self):
        return sum(len(f) for f in self.foundations) == 52
