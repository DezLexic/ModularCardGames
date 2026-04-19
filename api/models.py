from __future__ import annotations

from pydantic import BaseModel

from core.card import Card
from core.base_game import BaseGame
from core.types import GameState


# ── Request models ──────────────────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    game: str


class ActionRequest(BaseModel):
    action: str  # validated in SessionStore, not Pydantic


# ── Response models ──────────────────────────────────────────────────────────

class CardModel(BaseModel):
    rank: str
    suit: str


class RoundResultModel(BaseModel):
    outcome: str
    message: str


class GameStateResponse(BaseModel):
    session_id: str
    phase: str
    visible_cards: list[CardModel]
    message: str
    extra: dict
    valid_actions: list[str]
    is_round_over: bool
    result: RoundResultModel | None


class GamesResponse(BaseModel):
    games: list[str]


class CreateSessionResponse(BaseModel):
    session_id: str
    state: GameStateResponse


# ── Helpers ──────────────────────────────────────────────────────────────────

def card_to_model(card: Card) -> CardModel:
    return CardModel(rank=card.rank, suit=card.suit)


def build_state_response(session_id: str, state: GameState, game: BaseGame) -> GameStateResponse:
    is_over = game.is_round_over()
    result = None
    if is_over:
        r = game.get_result()
        result = RoundResultModel(outcome=r.outcome, message=r.message)
    return GameStateResponse(
        session_id=session_id,
        phase=state.phase,
        visible_cards=[card_to_model(c) for c in state.visible_cards],
        message=state.message,
        extra=state.extra,
        valid_actions=[a.value for a in game.get_valid_actions()],
        is_round_over=is_over,
        result=result,
    )
