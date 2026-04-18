from core.card import Card
from core.deck import Deck


def test_default_deck_size():
    assert len(Deck()) == 52


def test_two_decks():
    assert len(Deck(n_decks=2)) == 104


def test_jokers_included():
    d = Deck(include_jokers=True)
    jokers = [c for c in d.cards if c.rank == 'Joker']
    assert len(jokers) == 1


def test_no_jokers_by_default():
    d = Deck()
    assert all(c.rank != 'Joker' for c in d.cards)


def test_draw_returns_card():
    assert isinstance(Deck().draw(), Card)


def test_draw_reduces_size():
    d = Deck()
    d.draw()
    assert len(d) == 51


def test_draw_empty_deck_returns_none():
    d = Deck()
    for _ in range(52):
        d.draw()
    assert d.draw() is None


def test_deck_is_shuffled():
    # Two fresh decks should not be in the same order (astronomically unlikely)
    d1, d2 = Deck(), Deck()
    assert [repr(c) for c in d1.cards] != [repr(c) for c in d2.cards]
