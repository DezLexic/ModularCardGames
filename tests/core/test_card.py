from core.card import Card


def test_repr():
    assert repr(Card('A', 'Hearts')) == "A of Hearts"


def test_value_ace():
    assert Card('A', 'Hearts').value() == 14


def test_value_king():
    assert Card('K', 'Spades').value() == 13


def test_value_queen():
    assert Card('Q', 'Clubs').value() == 12


def test_value_jack():
    assert Card('J', 'Diamonds').value() == 11


def test_value_ten():
    assert Card('10', 'Hearts').value() == 10


def test_value_number():
    assert Card('7', 'Clubs').value() == 7


def test_lt():
    assert Card('2', 'Hearts') < Card('K', 'Spades')


def test_not_lt_higher():
    assert not (Card('K', 'Spades') < Card('2', 'Hearts'))


def test_eq_same_rank_and_suit():
    assert Card('A', 'Hearts') == Card('A', 'Hearts')


def test_eq_different_suit():
    assert Card('A', 'Hearts') != Card('A', 'Spades')


def test_eq_different_rank():
    assert Card('A', 'Hearts') != Card('K', 'Hearts')


def test_hashable():
    s = {Card('A', 'Hearts'), Card('A', 'Hearts'), Card('K', 'Spades')}
    assert len(s) == 2
