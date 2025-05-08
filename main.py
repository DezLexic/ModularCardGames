from card import Card
from game import Game

# Regular hands (no jokers)
hand_straight = [
    Card('3', 'Hearts'),
    Card('4', 'Clubs'),
    Card('5', 'Diamonds'),
    Card('6', 'Spades'),
    Card('7', 'Hearts')
]

hand_pair = [
    Card('K', 'Hearts'),
    Card('K', 'Clubs'),
    Card('5', 'Diamonds'),
    Card('9', 'Spades'),
    Card('2', 'Hearts')
]

hand_fullhouse = [
    Card('K', 'Hearts'),
    Card('K', 'Clubs'),
    Card('K', 'Diamonds'),
    Card('9', 'Spades'),
    Card('9', 'Hearts')
]

hand_flush = [
    Card('2', 'Spades'),
    Card('6', 'Spades'),
    Card('9', 'Spades'),
    Card('J', 'Spades'),
    Card('K', 'Spades')
]

hand_four_kind = [
    Card('A', 'Hearts'),
    Card('A', 'Clubs'),
    Card('A', 'Diamonds'),
    Card('A', 'Spades'),
    Card('9', 'Hearts')
]

# Hands with jokers
joker = Card('Joker', 'Joker')

hand_straight_joker = [
    Card('3', 'Hearts'),
    Card('4', 'Clubs'),
    joker,
    Card('6', 'Spades'),
    Card('7', 'Hearts')
]

hand_pair_joker = [
    Card('K', 'Hearts'),
    joker,
    Card('5', 'Diamonds'),
    Card('9', 'Spades'),
    Card('2', 'Hearts')
]

hand_fullhouse_joker = [
    Card('K', 'Hearts'),
    Card('K', 'Clubs'),
    joker,
    Card('9', 'Spades'),
    Card('9', 'Hearts')
]

hand_flush_joker = [
    Card('2', 'Spades'),
    Card('6', 'Spades'),
    joker,
    Card('J', 'Spades'),
    Card('K', 'Spades')
]

hand_four_kind_joker = [
    Card('A', 'Hearts'),
    Card('A', 'Clubs'),
    joker,
    Card('A', 'Spades'),
    Card('9', 'Hearts')
]

# Create Game instance
game = Game()

# Run tests (non-joker)
print("Straight:", game.straight(hand_straight))         # True
print("Pair:", game.n_kind(hand_pair))                   # 'pair': True
print("Full House:", game.n_kind(hand_fullhouse))        # 'fullhouse': True
print("Flush:", game.flush(hand_flush))                  # True
print("Four of a Kind:", game.n_kind(hand_four_kind))    # 'four_of_kind': True

# Run tests (with joker logic)
print("\n-- Joker Hands --")
print("Straight (with Joker):", game.straight(hand_straight_joker))  # True (joker as 5)
print("Pair (with Joker):", game.n_kind(hand_pair_joker))            # 'pair': True (joker as second K)
print("Full House (with Joker):", game.n_kind(hand_fullhouse_joker))# 'fullhouse': True (joker as third K)
print("Flush (with Joker):", game.flush(hand_flush_joker))          # True (joker counts as Spade)
print("Four of a Kind (with Joker):", game.n_kind(hand_four_kind_joker))  # 'four_of_kind': True
