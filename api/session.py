from __future__ import annotations

import time
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


class SessionCapError(Exception):
    pass


class SessionStore:
    SESSION_TTL_SECONDS: float = 7200.0  # 2 hours
    MAX_SESSIONS: int = 500

    def __init__(self) -> None:
        # dict[session_id, (game, state, last_accessed_monotonic)]
        self._sessions: dict[str, tuple[BaseGame, GameState, float]] = {}

    def create(self, game_name: str) -> tuple[str, GameState]:
        if len(self._sessions) >= self.MAX_SESSIONS:
            raise SessionCapError(f"Session limit ({self.MAX_SESSIONS}) reached")
        try:
            game = GameRegistry.get(game_name)
        except KeyError:
            raise UnknownGameError(f"No game named '{game_name}'")
        session_id = str(uuid4())
        state = game.start_round()
        self._sessions[session_id] = (game, state, time.monotonic())
        return session_id, state

    def get_state(self, session_id: str) -> tuple[BaseGame, GameState]:
        entry = self._sessions.get(session_id)
        if entry is None:
            raise SessionNotFoundError(f"Session '{session_id}' not found")
        game, state, _ = entry
        return game, state

    def apply_action(self, session_id: str, action_str: str) -> tuple[BaseGame, GameState]:
        entry = self._sessions.get(session_id)
        if entry is None:
            raise SessionNotFoundError(f"Session '{session_id}' not found")
        game, _, _ = entry
        try:
            action = Action(action_str)
        except ValueError:
            raise InvalidActionError(f"'{action_str}' is not a recognized action")
        if action not in game.get_valid_actions():
            raise InvalidActionError(f"Action '{action_str}' not valid in this phase")
        state = game.apply_action(action)
        self._sessions[session_id] = (game, state, time.monotonic())
        return game, state

    def delete(self, session_id: str) -> None:
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session '{session_id}' not found")
        del self._sessions[session_id]

    def sweep_expired(self) -> int:
        now = time.monotonic()
        expired = [
            sid for sid, (_, _, ts) in self._sessions.items()
            if now - ts > self.SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    def __len__(self) -> int:
        return len(self._sessions)
