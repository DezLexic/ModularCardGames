import games.blackjack
import games.texas_holdem
from core.registry import GameRegistry
from core.types import Action


def test_registry_has_both_games():
    assert "blackjack" in GameRegistry.available()
    assert "texas_holdem" in GameRegistry.available()


def test_blackjack_full_round_via_registry():
    game = GameRegistry.get("blackjack")
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.is_round_over()
    assert game.get_result().outcome in ("WIN", "LOSE", "PUSH")


def test_texas_holdem_fold_via_registry():
    game = GameRegistry.get("texas_holdem")
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.is_round_over()
    assert game.get_result().outcome == "FOLD"
