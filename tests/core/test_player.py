from core.card import Card
from core.player import Player


def test_default_name():
    assert Player().name == "Player"


def test_custom_name():
    assert Player("Alice").name == "Alice"


def test_starts_with_empty_hand():
    assert Player().hand == []


def test_receive_card():
    p = Player()
    c = Card('A', 'Hearts')
    p.receive_card(c)
    assert c in p.hand


def test_receive_multiple_cards():
    p = Player()
    p.receive_card(Card('A', 'Hearts'))
    p.receive_card(Card('K', 'Spades'))
    assert len(p.hand) == 2


def test_clear_hand():
    p = Player()
    p.receive_card(Card('A', 'Hearts'))
    p.clear_hand()
    assert p.hand == []
