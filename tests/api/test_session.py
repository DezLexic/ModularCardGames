import pytest
import games.blackjack  # noqa: F401 — triggers registration
import games.texas_holdem  # noqa: F401

from core.types import Action
from api.session import SessionStore, SessionNotFoundError, InvalidActionError, UnknownGameError


@pytest.fixture
def store():
    return SessionStore()


class TestCreate:
    def test_create_returns_session_id_and_state(self, store):
        session_id, state = store.create("blackjack")
        assert session_id
        assert state.phase == "PLAYER_TURN"

    def test_create_unknown_game_raises(self, store):
        with pytest.raises(UnknownGameError):
            store.create("no_such_game")

    def test_create_increments_length(self, store):
        store.create("blackjack")
        store.create("blackjack")
        assert len(store) == 2


class TestGetState:
    def test_get_state_returns_game_and_state(self, store):
        session_id, _ = store.create("blackjack")
        from core.base_game import BaseGame
        game, state = store.get_state(session_id)
        assert isinstance(game, BaseGame)
        assert state.phase == "PLAYER_TURN"

    def test_get_state_unknown_id_raises(self, store):
        with pytest.raises(SessionNotFoundError):
            store.get_state("nonexistent-id")


class TestApplyAction:
    def test_apply_action_updates_stored_state(self, store):
        session_id, _ = store.create("blackjack")
        _, new_state = store.apply_action(session_id, "HIT")
        _, stored_state = store.get_state(session_id)
        assert stored_state is new_state

    def test_apply_valid_action_returns_new_state(self, store):
        session_id, _ = store.create("blackjack")
        game, state = store.apply_action(session_id, "HIT")
        assert state is not None

    def test_apply_invalid_action_string_raises(self, store):
        session_id, _ = store.create("blackjack")
        with pytest.raises(InvalidActionError):
            store.apply_action(session_id, "NOT_AN_ACTION")

    def test_apply_wrong_phase_action_raises(self, store):
        session_id, _ = store.create("blackjack")
        with pytest.raises(InvalidActionError, match="not valid in this phase"):
            store.apply_action(session_id, "CALL")  # CALL is Texas Hold'em only

    def test_apply_action_unknown_session_raises(self, store):
        with pytest.raises(SessionNotFoundError):
            store.apply_action("nonexistent-id", "HIT")


class TestDelete:
    def test_delete_removes_session(self, store):
        session_id, _ = store.create("blackjack")
        store.delete(session_id)
        with pytest.raises(SessionNotFoundError):
            store.get_state(session_id)

    def test_delete_unknown_id_raises(self, store):
        with pytest.raises(SessionNotFoundError):
            store.delete("nonexistent-id")
