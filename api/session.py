from __future__ import annotations

from uuid import uuid4

from core.base_game import BaseGame
from core.registry import GameRegistry
from core.types import Action, GameState


class SessionNotFoundError(Exception):
    pass


class InvalidActionError(Exception):
    pass


class UnknownGameError(Exception):
    pass


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, tuple[BaseGame, GameState]] = {}

    def create(self, game_name: str) -> tuple[str, GameState]:
        try:
            game = GameRegistry.get(game_name)
        except KeyError:
            raise UnknownGameError(f"No game named '{game_name}'")
        session_id = str(uuid4())
        state = game.start_round()
        self._sessions[session_id] = (game, state)
        return session_id, state

    def get_state(self, session_id: str) -> tuple[BaseGame, GameState]:
        entry = self._sessions.get(session_id)
        if entry is None:
            raise SessionNotFoundError(session_id)
        return entry

    def apply_action(self, session_id: str, action_str: str) -> tuple[BaseGame, GameState]:
        game, _ = self.get_state(session_id)
        try:
            action = Action(action_str)
        except ValueError:
            raise InvalidActionError(f"'{action_str}' is not a recognized action")
        if action not in game.get_valid_actions():
            raise InvalidActionError(f"Action '{action_str}' not valid in this phase")
        state = game.apply_action(action)
        self._sessions[session_id] = (game, state)
        return game, state

    def delete(self, session_id: str) -> None:
        if session_id not in self._sessions:
            raise SessionNotFoundError(session_id)
        del self._sessions[session_id]

    def __len__(self) -> int:
        return len(self._sessions)
