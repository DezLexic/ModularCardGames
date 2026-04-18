from core.card import Card
from core.types import Action
from games.texas_holdem.rules import HandRank, bot_action, best_hand, evaluate_hand


# --- evaluate_hand ---

def test_royal_flush():
    cards = [Card('10','H'), Card('J','H'), Card('Q','H'), Card('K','H'), Card('A','H')]
    assert evaluate_hand(cards) == HandRank.ROYAL_FLUSH


def test_straight_flush():
    cards = [Card('5','C'), Card('6','C'), Card('7','C'), Card('8','C'), Card('9','C')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT_FLUSH


def test_four_of_a_kind():
    cards = [Card('A','H'), Card('A','D'), Card('A','C'), Card('A','S'), Card('K','H')]
    assert evaluate_hand(cards) == HandRank.FOUR_OF_A_KIND


def test_full_house():
    cards = [Card('K','H'), Card('K','D'), Card('K','C'), Card('Q','H'), Card('Q','D')]
    assert evaluate_hand(cards) == HandRank.FULL_HOUSE


def test_flush():
    cards = [Card('2','H'), Card('5','H'), Card('9','H'), Card('J','H'), Card('K','H')]
    assert evaluate_hand(cards) == HandRank.FLUSH


def test_straight():
    cards = [Card('5','H'), Card('6','D'), Card('7','C'), Card('8','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT


def test_ace_low_straight():
    cards = [Card('A','H'), Card('2','D'), Card('3','C'), Card('4','S'), Card('5','H')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT


def test_three_of_a_kind():
    cards = [Card('7','H'), Card('7','D'), Card('7','C'), Card('2','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.THREE_OF_A_KIND


def test_two_pair():
    cards = [Card('J','H'), Card('J','D'), Card('9','C'), Card('9','S'), Card('A','H')]
    assert evaluate_hand(cards) == HandRank.TWO_PAIR


def test_pair():
    cards = [Card('A','H'), Card('A','D'), Card('3','C'), Card('7','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.PAIR


def test_high_card():
    cards = [Card('2','H'), Card('5','D'), Card('7','C'), Card('9','S'), Card('J','H')]
    assert evaluate_hand(cards) == HandRank.HIGH_CARD


def test_hand_rank_ordering():
    assert HandRank.HIGH_CARD < HandRank.PAIR < HandRank.TWO_PAIR
    assert HandRank.TWO_PAIR < HandRank.THREE_OF_A_KIND < HandRank.STRAIGHT
    assert HandRank.STRAIGHT < HandRank.FLUSH < HandRank.FULL_HOUSE
    assert HandRank.FULL_HOUSE < HandRank.FOUR_OF_A_KIND < HandRank.STRAIGHT_FLUSH
    assert HandRank.STRAIGHT_FLUSH < HandRank.ROYAL_FLUSH


# --- best_hand ---

def test_best_hand_finds_royal_flush_in_seven_cards():
    cards = [
        Card('10','H'), Card('J','H'), Card('Q','H'), Card('K','H'), Card('A','H'),
        Card('2','D'), Card('3','C'),
    ]
    rank, _ = best_hand(cards)
    assert rank == HandRank.ROYAL_FLUSH


def test_best_hand_returns_five_cards():
    cards = [
        Card('2','H'), Card('5','D'), Card('7','C'), Card('9','S'), Card('J','H'),
        Card('3','D'), Card('4','C'),
    ]
    rank, combo = best_hand(cards)
    assert len(combo) == 5


# --- bot_action pre-flop ---

def test_bot_raises_on_pocket_pair():
    hole = [Card('A','H'), Card('A','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.RAISE


def test_bot_raises_on_ace_high():
    hole = [Card('A','H'), Card('7','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.RAISE


def test_bot_calls_on_medium_cards():
    hole = [Card('9','H'), Card('8','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.CALL


def test_bot_folds_weak_pre_flop():
    hole = [Card('2','H'), Card('7','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.FOLD


# --- bot_action post-flop ---

def test_bot_raises_strong_post_flop():
    hole = [Card('A','H'), Card('A','D')]
    community = [Card('A','C'), Card('K','S'), Card('2','H')]
    assert bot_action(hole, community, "FLOP") == Action.RAISE


def test_bot_calls_pair_post_flop():
    hole = [Card('9','H'), Card('3','D')]
    community = [Card('9','C'), Card('2','S'), Card('7','H')]
    assert bot_action(hole, community, "FLOP") == Action.CALL


def test_bot_folds_weak_post_flop():
    hole = [Card('2','H'), Card('7','D')]
    community = [Card('A','C'), Card('K','S'), Card('Q','H')]
    assert bot_action(hole, community, "FLOP") == Action.FOLD
