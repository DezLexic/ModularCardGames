# card.py

class Card:
    RANK_VALUES = {
        'A': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 11, 'Q': 12, 'K': 13
    }
    
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def value(self):
        return self.RANK_VALUES[self.rank]
    
    # defining this method allows us to use card.sort()
    def __lt__(self, other):
        return self.value() < other.value()

    def __eq__(self, other):
        return self.value() == other.value()
    
    # if you dont have access to class object create method in game