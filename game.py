from deck import Deck
from player import Player
from collections import defaultdict

class Game:
    def __init__(self, num_players=2):
        self.deck = Deck()
        # self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        self.community_cards = []
    
    def rank_count(self, cards):
        # hand = player.hand.sort(reversed=True)
        rank_counts = defaultdict(int)

        for card in cards:
            rank_counts[card.rank] += 1
        return rank_counts
    
    def n_kind(self, cards):
        jokers = [card for card in cards if card.rank == 'Joker']
        non_jokers = [card for card in cards if card.rank != 'Joker']
        joker_count = len(jokers)
        
        counts = self.rank_count(non_jokers)
        sorted_counts = sorted(counts.values(), reverse = True)
        # has_pair = any(count == 2 for count in counts.values())
        # three_of_kind = any(count == 3 for count in counts.values())
        # four_of_kind = any(count == 4 for count in counts.values())
        # fullhouse = has_pair and three_of_kind
        
        has_pair = False
        three_of_kind = False
        four_of_kind = False
        fullhouse = False
        
        
        for count in sorted_counts:
            if count == 4:
                four_of_kind = True
            elif count == 3:
                if joker_count == 2:
                    fullhouse = True
                    joker_count -= 2
                elif joker_count == 1:
                    four_of_kind = True
                    joker_count -= 1
                else:
                    three_of_kind = True
            elif count == 2:
                if joker_count >= 2:
                    fullhouse = True
                    joker_count -= 2
                elif joker_count == 1:
                    three_of_kind = True
                    joker_count -= 1
                else:
                    has_pair = True
            else:
                if joker_count == 1:
                    has_pair = True
                    joker_count -= 1
     
        if has_pair and three_of_kind:
            fullhouse = True
        
        return {
        'pair': has_pair,
        'three_of_kind': three_of_kind,
        'four_of_kind': four_of_kind,
        'fullhouse': fullhouse
        }
        
    # def suit_count(self, cards):
    #     suit_counts = defaultdict(int)

    #     for card in cards:
    #         suit_counts[card.suit] += 1
    #     return suit_counts
    
    def flush(self, cards):
        jokers = [card for card in cards if card.rank == 'Joker']
        non_jokers = [card for card in cards if card.rank != 'Joker']
    
        #set creates a list of unique items.                 
        suits = set(card.suit for card in non_jokers)
        return len(suits) == 1
    
    def straight(self, cards):
        jokers = [card for card in cards if card.rank == 'Joker']
        non_jokers = [card for card in cards if card.rank != 'Joker']
        
        gaps = 0
        
        ranks = sorted(set(card.value() for card in non_jokers))
        if len(ranks) + len(jokers) != 5:
            return False
        
        for i in range(len(ranks) - 1): # -1 so it doesnt do the last
            gaps += ranks[i+1] - ranks[i] - 1 #minus 1 so gap stays zero
        
        return gaps == len(jokers)
        
    
    def royal_flush(self, cards):
        # Step 1: Check for flush
        if not self.flush(cards):
            return False

        # Step 2: Extract the ranks
        jokers = [card for card in cards if card.rank == 'Joker']
        non_jokers = [card for card in cards if card.rank != 'Joker']
        
        ranks = set(card.rank for card in non_jokers)
        required_ranks = {'10', 'J', 'Q', 'K', 'A'}
        
        missing_ranks = required_ranks - ranks

        return len(missing_ranks) == len(jokers)
    
    def hand_results(self, cards):
        is_flush = self.flush(cards)
        is_straight = self.straight(cards)
        kinds = self.n_kind(cards)

        if kinds['four_of_kind']:
            return "Four of a Kind"
        elif kinds['fullhouse']:
            return "Full House"
        elif is_flush:
            return "Flush"
        elif is_straight:
            return "Straight"
        elif kinds['three_of_kind']:
            return "Three of a Kind"
        elif kinds['pair']:
            return "Pair"
        else:
            # If none match, return High Card with highest value
            highest_card = max(cards, key=lambda card: card.value())
            return f"High Card: {highest_card.rank}"
        
    
    # def sort_cards(cards):
    #     return cards.sort(key=lambda card: RANK_VALUES[card['rank']], reverse=True)