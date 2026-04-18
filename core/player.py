from core.card import Card


class Player:
    def __init__(self, name: str = "Player") -> None:
        self.name = name
        self.hand: list[Card] = []

    def receive_card(self, card: Card) -> None:
        self.hand.append(card)

    def clear_hand(self) -> None:
        self.hand = []
