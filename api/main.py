from __future__ import annotations

import games.blackjack  # noqa: F401 — triggers registration
import games.texas_holdem  # noqa: F401

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from api.models import (
    ActionRequest,
    CreateSessionRequest,
    CreateSessionResponse,
    GameStateResponse,
    GamesResponse,
    build_state_response,
)
from api.session import (
    InvalidActionError,
    SessionNotFoundError,
    SessionStore,
    UnknownGameError,
)
from core.registry import GameRegistry

app = FastAPI(title="Modular Card Games API")
_store = SessionStore()


@app.get("/games", response_model=GamesResponse)
def get_games() -> GamesResponse:
    return GamesResponse(games=GameRegistry.available())


@app.post("/sessions", response_model=CreateSessionResponse, status_code=201)
def create_session(body: CreateSessionRequest) -> CreateSessionResponse:
    try:
        session_id, state = _store.create(body.game)
    except UnknownGameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    game, _ = _store.get_state(session_id)
    return CreateSessionResponse(
        session_id=session_id,
        state=build_state_response(session_id, state, game),
    )


@app.get("/sessions/{session_id}", response_model=GameStateResponse)
def get_session(session_id: str) -> GameStateResponse:
    try:
        game, state = _store.get_state(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return build_state_response(session_id, state, game)


@app.post("/sessions/{session_id}/action", response_model=GameStateResponse)
def apply_action(session_id: str, body: ActionRequest) -> GameStateResponse:
    try:
        game, state = _store.apply_action(session_id, body.action)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return build_state_response(session_id, state, game)


@app.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str) -> Response:
    try:
        _store.delete(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(status_code=204)
