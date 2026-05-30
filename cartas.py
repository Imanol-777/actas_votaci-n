
SUITS = ["spades", "hearts", "diamonds", "clubs"]
SUIT_SYMBOL = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}
SUIT_NAME_ES = {
    "spades": "Picas",
    "hearts": "Corazones",
    "diamonds": "Diamantes",
    "clubs": "Tréboles",
}
RED_SUITS = {"hearts", "diamonds"}

# 1 = As ... 11 = J, 12 = Q, 13 = K
RANK_LABEL = {1: "A", 11: "J", 12: "Q", 13: "K"}
for _r in range(2, 11):
    RANK_LABEL[_r] = str(_r)


class Carta:

    __slots__ = ("rank", "suit", "face_up")

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.face_up = False

    @property
    def color(self):
        return "red" if self.suit in RED_SUITS else "black"

    @property
    def label(self):
        return RANK_LABEL[self.rank]

    @property
    def symbol(self):
        return SUIT_SYMBOL[self.suit]

    def __repr__(self):
        return "Carta(%s%s%s)" % (
            self.label, self.symbol, "" if self.face_up else "*"
        )
