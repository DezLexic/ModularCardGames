import pytest
from core.card import Card
from core.types import Action
from games.texas_holdem.game import TexasHoldemGame


def test_start_round_phase_is_pre_flop():
    game = TexasHoldemGame()
    state = game.start_round()
    assert state.phase == "PRE_FLOP"


def test_start_round_deals_two_hole_cards_each():
    game = TexasHoldemGame()
    game.start_round()
    assert len(game._player.hand) == 2
    assert len(game._bot.hand) == 2


def test_no_community_cards_at_start():
    game = TexasHoldemGame()
    game.start_round()
    assert game._community == []


def test_pre_flop_valid_actions():
    game = TexasHoldemGame()
    game.start_round()
    actions = game.get_valid_actions()
    assert Action.FOLD in actions
    assert Action.CALL in actions
    assert Action.RAISE in actions


def test_fold_ends_round_immediately():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.is_round_over() is True


def test_fold_result_is_fold():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.get_result().outcome == "FOLD"


def test_call_pre_flop_advances_to_flop_or_ends():
    game = TexasHoldemGame()
    game.start_round()
    # Give bot strong cards so it won't fold
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    state = game.apply_action(Action.CALL)
    assert state.phase in ("FLOP", "ROUND_OVER")


def test_flop_deals_three_community_cards():
    game = TexasHoldemGame()
    game.start_round()
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    game.apply_action(Action.CALL)
    if not game.is_round_over():
        assert len(game._community) == 3


def test_full_round_reaches_valid_result():
    game = TexasHoldemGame()
    game.start_round()
    # Give bot a pair so it won't fold at any phase
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    while not game.is_round_over():
        actions = game.get_valid_actions()
        action = Action.CHECK if Action.CHECK in actions else Action.CALL
        game.apply_action(action)
    assert game.get_result().outcome in ("WIN", "LOSE", "PUSH")


def test_result_raises_before_round_over():
    game = TexasHoldemGame()
    game.start_round()
    with pytest.raises(RuntimeError):
        game.get_result()


def test_start_round_resets_state():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.is_round_over() is True
    game.start_round()
    assert game.is_round_over() is False
    assert game._community == []


def test_state_extra_contains_player_hand_and_community():
    game = TexasHoldemGame()
    state = game.start_round()
    assert "player_hand" in state.extra
    assert "community_cards" in state.extra
