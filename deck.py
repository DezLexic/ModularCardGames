import random
from card import Card

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.cards.append(Card('Joker', 'Joker'))
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None
    
    # print("✅ deck.py loaded!")
    # print("Deck is defined:", 'Deck' in globals())