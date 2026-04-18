import pytest
from core.base_game import BaseGame
from core.registry import GameRegistry
from core.types import Action, GameState, RoundResult


class _FakeGame(BaseGame):
    def start_round(self) -> GameState:
        return GameState(phase="TEST", visible_cards=[], message="ok")

    def get_valid_actions(self) -> list[Action]:
        return [Action.HIT]

    def apply_action(self, action: Action) -> GameState:
        return self.start_round()

    def is_round_over(self) -> bool:
        return True

    def get_result(self) -> RoundResult:
        return RoundResult(outcome="WIN", message="win")


def test_register_and_get_returns_instance():
    GameRegistry.register("fake", _FakeGame)
    game = GameRegistry.get("fake")
    assert isinstance(game, _FakeGame)


def test_available_lists_registered_games():
    GameRegistry.register("fake_a", _FakeGame)
    GameRegistry.register("fake_b", _FakeGame)
    assert "fake_a" in GameRegistry.available()
    assert "fake_b" in GameRegistry.available()


def test_get_unknown_game_raises_key_error():
    with pytest.raises(KeyError, match="no_such_game"):
        GameRegistry.get("no_such_game")


def test_get_returns_new_instance_each_time():
    GameRegistry.register("fake", _FakeGame)
    assert GameRegistry.get("fake") is not GameRegistry.get("fake")


def test_base_game_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseGame()  # type: ignore
