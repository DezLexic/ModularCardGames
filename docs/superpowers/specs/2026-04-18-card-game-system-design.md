# Modular Card Game System — Design Spec
_Date: 2026-04-18_

## Context

The existing codebase has loose, unconnected Python classes (Card, Deck, Player, Game, Table) with poker hand evaluation logic. The goal is to restructure this into a modular card game engine that supports Texas Hold'em and Blackjack today, and is cleanly expandable to new games in the future. The immediate deliverable is a pure game logic engine (no UI). The long-term target is to serve this from a portfolio website, so all game state must be JSON-serializable from day one.

---

## Architecture

**Pattern:** Abstract Base Class + Registry (Strategy Pattern)

Each game implements a shared `BaseGame` interface. A `GameRegistry` maps game names to classes. A thin runner selects a game and drives the loop. Adding a new game = one new subpackage + registration.

### Directory Structure

```
ModularCardGames/
├── core/
│   ├── __init__.py
│   ├── card.py          # Card (refactored from existing)
│   ├── deck.py          # Deck (refactored, supports N decks)
│   ├── player.py        # Player (refactored)
│   ├── base_game.py     # BaseGame ABC
│   ├── registry.py      # GameRegistry
│   └── types.py         # GameState, Action, RoundResult dataclasses
├── games/
│   ├── __init__.py
│   ├── blackjack/
│   │   ├── __init__.py
│   │   ├── game.py      # BlackjackGame(BaseGame)
│   │   └── rules.py     # Hand value calc, dealer AI
│   └── texas_holdem/
│       ├── __init__.py
│       ├── game.py      # TexasHoldemGame(BaseGame)
│       └── rules.py     # Hand evaluation (migrated from game.py), bot heuristics
├── tests/
│   ├── conftest.py
│   ├── core/
│   │   ├── test_card.py
│   │   ├── test_deck.py
│   │   ├── test_player.py
│   │   └── test_registry.py
│   └── games/
│       ├── test_blackjack.py
│       └── test_texas_holdem.py
├── docs/
│   └── superpowers/specs/
├── main.py              # CLI runner: select game, play rounds
└── .claude/CLAUDE.md
```

---

## Core Types (`core/types.py`)

```python
@dataclass
class GameState:
    phase: str                  # e.g. "PLAYER_TURN", "FLOP"
    visible_cards: list[Card]   # cards the player can see
    message: str                # human-readable description
    extra: dict                 # game-specific data (JSON-serializable)

@dataclass
class RoundResult:
    outcome: str                # "WIN" | "LOSE" | "PUSH" | "FOLD"
    message: str

class Action(str, Enum):
    # Shared
    FOLD = "FOLD"
    # Blackjack
    HIT = "HIT"
    STAND = "STAND"
    DOUBLE = "DOUBLE"
    # Hold'em
    CALL = "CALL"
    RAISE = "RAISE"
    CHECK = "CHECK"
```

---

## BaseGame Interface (`core/base_game.py`)

```python
class BaseGame(ABC):
    @abstractmethod
    def start_round(self) -> GameState: ...

    @abstractmethod
    def get_valid_actions(self) -> list[Action]: ...

    @abstractmethod
    def apply_action(self, action: Action) -> GameState: ...

    @abstractmethod
    def is_round_over(self) -> bool: ...

    @abstractmethod
    def get_result(self) -> RoundResult: ...
```

`GameState.extra` carries game-specific data without polluting the base class (e.g., community cards in Hold'em, dealer upcard in Blackjack).

---

## GameRegistry (`core/registry.py`)

```python
class GameRegistry:
    _games: dict[str, type[BaseGame]] = {}

    @classmethod
    def register(cls, name: str, game_class: type[BaseGame]) -> None: ...

    @classmethod
    def get(cls, name: str) -> BaseGame: ...

    @classmethod
    def available(cls) -> list[str]: ...
```

Games self-register in their `__init__.py`:
```python
GameRegistry.register("blackjack", BlackjackGame)
GameRegistry.register("texas_holdem", TexasHoldemGame)
```

---

## Blackjack (`games/blackjack/`)

### Phases
`DEAL → PLAYER_TURN → DEALER_TURN (auto) → SHOWDOWN → ROUND_OVER`

### rules.py
- `hand_value(cards) -> int` — calculates total (Ace = 1 or 11, whichever is better)
- `is_bust(cards) -> bool`
- `dealer_should_hit(cards) -> bool` — hit if total < 17
- `compare_hands(player, dealer) -> str` — returns "WIN" | "LOSE" | "PUSH"

### game.py
- `start_round()` — deals 2 to player, 2 to dealer (1 hidden), returns DEAL state
- `apply_action(HIT)` — deals 1 card to player; if bust → ROUND_OVER
- `apply_action(STAND)` — triggers DEALER_TURN, dealer plays to completion, then SHOWDOWN
- `apply_action(DOUBLE)` — deals 1 card, then triggers dealer turn
- Dealer AI runs automatically (no player action) using `dealer_should_hit()`

---

## Texas Hold'em (`games/texas_holdem/`)

### Phases
`PRE_FLOP → FLOP → TURN → RIVER → SHOWDOWN → ROUND_OVER`

Each phase: player acts, then bot acts (FOLD/CALL/RAISE/CHECK).

### rules.py
- `evaluate_hand(hole_cards, community_cards) -> HandRank` — migrated and cleaned up from existing `game.py`
- `best_hand(cards) -> tuple[HandRank, str]` — best 5-card combo from 7 cards
- `bot_action(hole_cards, community_cards, phase) -> Action` — heuristic: fold weak, call medium, raise strong

### game.py
- `start_round()` — deals 2 hole cards to player and bot, returns PRE_FLOP state
- `apply_action(FOLD)` — bot wins, ROUND_OVER
- `apply_action(CALL/CHECK/RAISE)` — bot responds via heuristic, advance to next phase
- At RIVER + player action: bot acts, then SHOWDOWN
- SHOWDOWN: `evaluate_hand()` for both, compare, return result

### Bot Heuristic (simple, v1)
- PRE_FLOP: raise on pairs/high cards (A,K,Q), call on medium, fold on low
- Post-flop: evaluate current hand strength, scale aggression accordingly

---

## Existing Code Migration

| Existing file | Destination |
|---|---|
| `card.py` | `core/card.py` (minor cleanup) |
| `deck.py` | `core/deck.py` (add `n_decks` param) |
| `player.py` | `core/player.py` (simplify to hand container) |
| `game.py` | `games/texas_holdem/rules.py` (hand eval logic) |
| `table.py` | Deleted (replaced by registry + game classes) |
| `main.py` | Rewritten as thin CLI runner |

---

## Testing Strategy (TDD)

Build order — write tests first at each layer before implementing:

1. **`core/` types** — Card comparisons, Deck draw/shuffle, Player hand management
2. **BaseGame contract** — Registry lookup, unknown game error, abstract method enforcement
3. **Blackjack rules** — `hand_value()`, bust detection, dealer AI, outcome comparison
4. **BlackjackGame flow** — full round sequences via `apply_action()`, edge cases (bust, push, double)
5. **Hold'em rules** — hand evaluation (migrated from existing tests in `main.py`), bot heuristic
6. **TexasHoldemGame flow** — phase transitions, fold shortcut, showdown resolution
7. **Integration** — `GameRegistry.get("blackjack").start_round()` through to `get_result()`

Test runner: `pytest tests/`  
Single test: `pytest tests/games/test_blackjack.py::test_bust_on_hit`

---

## Web-Readiness

- `GameState` and `RoundResult` are plain dataclasses — call `dataclasses.asdict()` to serialize
- `Action` is a string enum — safe to pass as JSON values
- `GameRegistry.available()` returns the game list for a future "select a game" API endpoint
- No I/O or print statements inside game classes — all output goes through `GameState.message`
