import pytest
from core.card import Card
from core.types import Action
from games.blackjack.game import BlackjackGame
from games.blackjack.rules import hand_value


def test_start_round_phase_is_player_turn():
    game = BlackjackGame()
    state = game.start_round()
    assert state.phase == "PLAYER_TURN"


def test_start_round_deals_two_cards_to_player():
    game = BlackjackGame()
    game.start_round()
    assert len(game._player.hand) == 2


def test_start_round_deals_two_cards_to_dealer():
    game = BlackjackGame()
    game.start_round()
    assert len(game._dealer_hand) == 2


def test_valid_actions_on_fresh_deal_include_double():
    game = BlackjackGame()
    game.start_round()
    actions = game.get_valid_actions()
    assert Action.HIT in actions
    assert Action.STAND in actions
    assert Action.DOUBLE in actions


def test_hit_adds_card_to_player():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.HIT)
    assert len(game._player.hand) == 3


def test_after_hit_double_not_in_valid_actions():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.HIT)
    assert Action.DOUBLE not in game.get_valid_actions()


def test_stand_ends_round():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.is_round_over() is True


def test_stand_result_is_win_lose_or_push():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.get_result().outcome in ("WIN", "LOSE", "PUSH")


def test_bust_on_hit_ends_round_with_lose():
    game = BlackjackGame()
    game.start_round()
    game._player.hand = [Card('10', 'H'), Card('10', 'C')]
    game._phase = "PLAYER_TURN"
    game._deck.cards.append(Card('10', 'D'))  # next draw = bust
    game.apply_action(Action.HIT)
    assert game.is_round_over() is True
    assert game.get_result().outcome == "LOSE"


def test_double_deals_one_card_then_ends():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.DOUBLE)
    assert game.is_round_over() is True
    assert len(game._player.hand) == 3


def test_result_raises_before_round_over():
    game = BlackjackGame()
    game.start_round()
    with pytest.raises(RuntimeError):
        game.get_result()


def test_state_hides_dealer_hole_card_during_player_turn():
    game = BlackjackGame()
    game.start_round()
    state = game._state()
    assert len(state.extra["dealer_visible"]) == 1


def test_state_reveals_full_dealer_hand_after_stand():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    state = game._state()
    assert len(state.extra["dealer_visible"]) == len(game._dealer_hand)


def test_start_round_resets_previous_round():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.is_round_over() is True
    game.start_round()
    assert game.is_round_over() is False
