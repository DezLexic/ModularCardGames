from card import Card


class Player:
    def __init__(self):
        self.hand = []
        self.wins = 0
        self.loses = 0
    
    def won(self):
        self.wins += 1
    
    def lose(self):
        self.loses += 1
        
    def clearHand(self):
        self.hand = []
        
   ##def join()
    
    