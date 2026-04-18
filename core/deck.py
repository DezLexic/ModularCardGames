import random
from core.card import Card

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


class Deck:
    def __init__(self, n_decks: int = 1, include_jokers: bool = False) -> None:
        self.cards = [
            Card(rank, suit)
            for _ in range(n_decks)
            for suit in SUITS
            for rank in RANKS
        ]
        if include_jokers:
            for _ in range(n_decks):
                self.cards.append(Card('Joker', 'Joker'))
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        return self.cards.pop() if self.cards else None

    def __len__(self) -> int:
        return len(self.cards)
