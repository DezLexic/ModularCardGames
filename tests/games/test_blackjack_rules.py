from core.card import Card
from games.blackjack.rules import compare_hands, dealer_should_hit, hand_value, is_bust


def test_hand_value_number_cards():
    assert hand_value([Card('7', 'H'), Card('8', 'C')]) == 15


def test_hand_value_face_cards_are_10():
    assert hand_value([Card('J', 'H'), Card('Q', 'C'), Card('K', 'S')]) == 30


def test_hand_value_ace_as_11():
    assert hand_value([Card('A', 'H'), Card('9', 'C')]) == 20


def test_hand_value_ace_drops_to_1_to_avoid_bust():
    assert hand_value([Card('A', 'H'), Card('9', 'C'), Card('5', 'D')]) == 15


def test_hand_value_blackjack():
    assert hand_value([Card('A', 'H'), Card('K', 'C')]) == 21


def test_hand_value_two_aces():
    # One ace = 11, second ace must = 1 to avoid bust
    assert hand_value([Card('A', 'H'), Card('A', 'D')]) == 12


def test_is_bust_over_21():
    assert is_bust([Card('10', 'H'), Card('Q', 'C'), Card('5', 'D')]) is True


def test_is_bust_exactly_21():
    assert is_bust([Card('A', 'H'), Card('K', 'C')]) is False


def test_is_bust_under_21():
    assert is_bust([Card('10', 'H'), Card('9', 'C')]) is False


def test_dealer_should_hit_at_16():
    assert dealer_should_hit([Card('9', 'H'), Card('7', 'C')]) is True


def test_dealer_should_not_hit_at_17():
    assert dealer_should_hit([Card('10', 'H'), Card('7', 'C')]) is False


def test_dealer_should_not_hit_above_17():
    assert dealer_should_hit([Card('10', 'H'), Card('9', 'C')]) is False


def test_compare_player_wins():
    player = [Card('10', 'H'), Card('9', 'C')]   # 19
    dealer = [Card('10', 'H'), Card('7', 'C')]   # 17
    assert compare_hands(player, dealer) == "WIN"


def test_compare_dealer_wins():
    player = [Card('10', 'H'), Card('7', 'C')]   # 17
    dealer = [Card('10', 'H'), Card('9', 'C')]   # 19
    assert compare_hands(player, dealer) == "LOSE"


def test_compare_push():
    player = [Card('10', 'H'), Card('8', 'C')]   # 18
    dealer = [Card('9', 'H'), Card('9', 'C')]    # 18
    assert compare_hands(player, dealer) == "PUSH"
