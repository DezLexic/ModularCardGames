# Modular Card Game

A modular card game engine in Python with a stateful FastAPI backend. Blackjack is live. Texas Hold'em is implemented and next to ship.

---

## Architecture

```
core/           — Cards, deck, player, abstract game contract, registry
games/
  blackjack/    — BlackjackGame + hand evaluation rules
  texas_holdem/ — TexasHoldemGame + poker hand ranking + bot heuristic
api/            — FastAPI session layer, HTTP routes, rate limiting
tests/          — Unit and integration tests
```

**Pattern:** Abstract Base Class + Registry (Strategy Pattern). Each game implements `BaseGame`. `GameRegistry` maps names to classes. Adding a new game = one new subpackage + one `register()` call.

---

## Core

### Types (`core/types.py`)

Three shared types flow through every game and the API:

- **`Action`** (str Enum) — `HIT`, `STAND`, `DOUBLE`, `FOLD`, `CALL`, `RAISE`, `CHECK`
- **`GameState`** — snapshot returned after every action: `phase`, `visible_cards`, `message`, `extra` (game-specific dict, always JSON-serializable)
- **`RoundResult`** — final outcome: `outcome` (`WIN`/`LOSE`/`PUSH`/`FOLD`) + `message`

`extra` is the extension point — games attach hand values, community cards, or dealer state without polluting the base type.

### BaseGame (`core/base_game.py`)

```python
class BaseGame(ABC):
    def start_round(self) -> GameState: ...
    def get_valid_actions(self) -> list[Action]: ...
    def apply_action(self, action: Action) -> GameState: ...
    def is_round_over(self) -> bool: ...
    def get_result(self) -> RoundResult: ...
```

State machine: `start_round` → repeated `apply_action` → `get_result`. Every method returns a new `GameState` — no implicit side effects visible to callers.

### Registry (`core/registry.py`)

```python
GameRegistry.register("blackjack", BlackjackGame)
GameRegistry.register("texas_holdem", TexasHoldemGame)
```

Games self-register on import. `GameRegistry.get(name)` instantiates and returns a fresh game. `GameRegistry.available()` lists registered names — used by `GET /games`.

### Card & Deck (`core/card.py`, `core/deck.py`)

`Card` is a hashable value object with rank/suit and a `RANK_VALUES` map (2–10, J=11, Q=12, K=13, A=14). Supports comparison and hashing for use in sets and sorted operations.

`Deck` takes `n_decks` (default 1) and auto-shuffles on creation. `draw()` pops from the top. Games manage deck lifecycle — no auto-reshuffle.

---

## Blackjack (`games/blackjack/`)

### Phases

`PLAYER_TURN → DEALER_TURN → ROUND_OVER`

### Rules (`rules.py`)

- `hand_value(cards)` — totals hand, counting Aces as 11 then downgrading to 1 as needed to stay ≤ 21
- `is_bust(cards)` — True if value > 21
- `dealer_should_hit(cards)` — True if value < 17 (standard dealer rules)
- `compare_hands(player, dealer)` — returns `"WIN"`, `"LOSE"`, or `"PUSH"`

### Game (`game.py`)

Uses a 6-deck shoe. Dealer's hole card is hidden until `DEALER_TURN`. After `STAND` or `DOUBLE`, the dealer auto-plays to completion — the client never drives the dealer turn.

Valid actions:
- `PLAYER_TURN` (2 cards): `HIT`, `STAND`, `DOUBLE`
- `PLAYER_TURN` (3+ cards): `HIT`, `STAND`

`extra` fields: `player_hand`, `player_value`, `dealer_visible`, `dealer_value` (only when round over).

---

## Texas Hold'em (`games/texas_holdem/`)

### Phases

`PRE_FLOP → FLOP → TURN → RIVER → SHOWDOWN → ROUND_OVER`

Each phase: player acts, then bot responds immediately.

### Rules (`rules.py`)

- `HandRank` (IntEnum) — `HIGH_CARD` (1) through `ROYAL_FLUSH` (10)
- `evaluate_hand(cards)` — ranks a 5-card hand; detects flush, straight, pairs, full house, etc. Handles ace-low straights (A-2-3-4-5)
- `best_hand(cards)` — brute-forces all `C(7,5) = 21` combinations from hole + community cards, returns best `HandRank`
- `bot_action(hole_cards, community_cards, phase)` — heuristic decision tree:
  - **Pre-flop:** raise on pair or A/K/Q; call on rank ≥ 9; fold otherwise
  - **Post-flop:** raise on three-of-a-kind+; call on pair+; fold on high card

### Game (`game.py`)

Single deck, renewed each round. Bot acts after every player action. `FOLD` ends the round immediately. Community cards are revealed incrementally (flop = 3, turn = 1, river = 1). `_resolve_showdown()` calls `best_hand()` for both players and compares.

`extra` fields: `player_hole`, `community_cards`, `phase`.

---

## API (`api/`)

### Session Layer (`session.py`)

`SessionStore` holds all live game state in memory:

```python
_sessions: dict[str, tuple[BaseGame, GameState, float]]
#                          ↑ game    ↑ state   ↑ monotonic timestamp
```

- **Cap:** 500 concurrent sessions (503 on overflow)
- **TTL:** 2-hour expiry via `time.monotonic()` timestamps
- **Sweep:** background asyncio task purges expired sessions every 5 minutes
- `get_state()` and `apply_action()` both refresh the TTL timestamp

Exceptions signal failure mode to the HTTP layer: `SessionNotFoundError`, `InvalidActionError`, `UnknownGameError`, `SessionCapError`.

### Routes (`main.py`)

| Method | Path | Rate limit | Description |
|--------|------|-----------|-------------|
| `GET` | `/games` | 120/min | List registered game names |
| `POST` | `/sessions` | 10/min | Create session, return initial state |
| `GET` | `/sessions/{id}` | 120/min | Fetch current state |
| `POST` | `/sessions/{id}/action` | 60/min | Apply action, return new state |
| `DELETE` | `/sessions/{id}` | 120/min | End session |

Rate limiting uses `slowapi` with `get_ipaddr` (reads `X-Forwarded-For` for proxy awareness). CORS origins are configured via the `ALLOWED_ORIGINS` environment variable — wildcards are blocked when credentials are enabled.

### Serialization (`models.py`)

`build_state_response()` is the single conversion point from game state to HTTP response. All `Card` objects become `CardModel` (rank + suit). `GameStateResponse` includes `valid_actions` and `is_round_over` so clients never need to inspect phase strings directly.

---

## Testing

```
tests/
  core/   — Card, Deck, Player, Registry unit tests
  games/  — Blackjack and Hold'em flow tests (full round sequences)
  api/    — HTTP route tests, session lifecycle, rate limiting, CORS
```

Run: `pytest tests/`
