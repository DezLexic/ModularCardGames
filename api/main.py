from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import games.blackjack  # noqa: F401
import games.texas_holdem  # noqa: F401

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_ipaddr

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
    SessionCapError,
    SessionNotFoundError,
    SessionStore,
    UnknownGameError,
)
from core.registry import GameRegistry

# ── Logging ───────────────────────────────────────────────────────────────────

_logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_ipaddr)

# ── Session store ─────────────────────────────────────────────────────────────

_store = SessionStore()


# ── Background sweep ──────────────────────────────────────────────────────────

async def _sweep_loop() -> None:
    while True:
        await asyncio.sleep(300)  # every 5 minutes
        try:
            _store.sweep_expired()
        except Exception:
            _logger.exception("sweep_expired raised an unexpected error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_sweep_loop())
    yield
    task.cancel()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Modular Card Games API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_allowed_origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

if "*" in _allowed_origins:
    raise ValueError(
        "ALLOWED_ORIGINS='*' is incompatible with allow_credentials=True. "
        "Set explicit origins (e.g. https://yoursite.vercel.app) instead."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/games", response_model=GamesResponse)
@limiter.limit("120/minute")
def get_games(request: Request) -> GamesResponse:
    return GamesResponse(games=GameRegistry.available())


@app.post("/sessions", response_model=CreateSessionResponse, status_code=201)
@limiter.limit("10/minute")
def create_session(request: Request, body: CreateSessionRequest) -> CreateSessionResponse:
    try:
        session_id, state = _store.create(body.game)
    except SessionCapError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except UnknownGameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        game, _ = _store.get_state(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=500, detail="Session unavailable after creation")
    return CreateSessionResponse(
        session_id=session_id,
        state=build_state_response(session_id, state, game),
    )


@app.get("/sessions/{session_id}", response_model=GameStateResponse)
@limiter.limit("120/minute")
def get_session(request: Request, session_id: str) -> GameStateResponse:
    try:
        game, state = _store.get_state(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return build_state_response(session_id, state, game)


@app.post("/sessions/{session_id}/action", response_model=GameStateResponse)
@limiter.limit("60/minute")
def apply_action(request: Request, session_id: str, body: ActionRequest) -> GameStateResponse:
    try:
        game, state = _store.apply_action(session_id, body.action)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return build_state_response(session_id, state, game)


@app.delete("/sessions/{session_id}", status_code=204)
@limiter.limit("120/minute")
def delete_session(request: Request, session_id: str) -> Response:
    try:
        _store.delete(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(status_code=204)
