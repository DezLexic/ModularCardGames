# Card Game System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the existing loose Python classes into a modular card game engine supporting Blackjack and Texas Hold'em, expandable to future games via a registry pattern.

**Architecture:** Each game subclasses `BaseGame` (ABC) and self-registers with `GameRegistry`. All game state flows through JSON-serializable `GameState` / `RoundResult` dataclasses, ready for a future web layer. Tests are written before implementation at every layer.

**Tech Stack:** Python 3.10+, pytest

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `core/__init__.py` | Package marker |
| Create | `core/types.py` | `Action`, `GameState`, `RoundResult` |
| Create | `core/card.py` | `Card` class (migrated + fixed) |
| Create | `core/deck.py` | `Deck` class (migrated + `n_decks`, `include_jokers`) |
| Create | `core/player.py` | `Player` class (simplified) |
| Create | `core/base_game.py` | `BaseGame` ABC |
| Create | `core/registry.py` | `GameRegistry` |
| Create | `games/__init__.py` | Package marker |
| Create | `games/blackjack/__init__.py` | Registers `BlackjackGame` |
| Create | `games/blackjack/rules.py` | `hand_value`, `is_bust`, `dealer_should_hit`, `compare_hands` |
| Create | `games/blackjack/game.py` | `BlackjackGame(BaseGame)` |
| Create | `games/texas_holdem/__init__.py` | Registers `TexasHoldemGame` |
| Create | `games/texas_holdem/rules.py` | `HandRank`, `evaluate_hand`, `best_hand`, `bot_action` |
| Create | `games/texas_holdem/game.py` | `TexasHoldemGame(BaseGame)` |
| Rewrite | `main.py` | CLI runner: select game, play loop |
| Create | `tests/__init__.py` | Package marker |
| Create | `tests/conftest.py` | `reset_registry` fixture |
| Create | `tests/core/__init__.py` | Package marker |
| Create | `tests/core/test_card.py` | Card tests |
| Create | `tests/core/test_deck.py` | Deck tests |
| Create | `tests/core/test_player.py` | Player tests |
| Create | `tests/core/test_registry.py` | Registry tests |
| Create | `tests/games/__init__.py` | Package marker |
| Create | `tests/games/test_blackjack.py` | Blackjack rules + game flow tests |
| Create | `tests/games/test_texas_holdem.py` | Hold'em rules + game flow tests |
| Create | `pytest.ini` | Test discovery config |
| Delete | `table.py` | Replaced by registry pattern |

---

## Task 1: Project Scaffolding

**Files:**
- Create: all `__init__.py` and directory files listed above
- Create: `pytest.ini`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p core games/blackjack games/texas_holdem tests/core tests/games
```

- [ ] **Step 2: Create all `__init__.py` files**

```bash
touch core/__init__.py games/__init__.py games/blackjack/__init__.py games/texas_holdem/__init__.py tests/__init__.py tests/core/__init__.py tests/games/__init__.py
```

- [ ] **Step 3: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
pythonpath = .
```

- [ ] **Step 4: Install pytest**

```bash
pip install pytest
```

- [ ] **Step 5: Delete `table.py`**

```bash
rm table.py
```

- [ ] **Step 6: Verify pytest runs (no tests yet)**

```bash
pytest
```
Expected: `no tests ran`

- [ ] **Step 7: Commit**

```bash
git add core/ games/ tests/ pytest.ini
git commit -m "chore: scaffold package structure and pytest config"
```

---

## Task 2: Core Types

**Files:**
- Create: `core/types.py`

- [ ] **Step 1: Write failing import test**

Create `tests/core/test_types.py`:
```python
from core.types import Action, GameState, RoundResult

def test_action_values():
    assert Action.HIT == "HIT"
    assert Action.FOLD == "FOLD"
    assert Action.STAND == "STAND"
    assert Action.DOUBLE == "DOUBLE"
    assert Action.CALL == "CALL"
    assert Action.RAISE == "RAISE"
    assert Action.CHECK == "CHECK"

def test_game_state_fields():
    state = GameState(phase="TEST", visible_cards=[], message="hello", extra={})
    assert state.phase == "TEST"
    assert state.visible_cards == []
    assert state.message == "hello"
    assert state.extra == {}

def test_game_state_extra_defaults_empty():
    state = GameState(phase="X", visible_cards=[], message="y")
    assert state.extra == {}

def test_round_result_fields():
    result = RoundResult(outcome="WIN", message="You win!")
    assert result.outcome == "WIN"
    assert result.message == "You win!"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_types.py -v
```
Expected: `ModuleNotFoundError: No module named 'core.types'`

- [ ] **Step 3: Implement `core/types.py`**

```python
from dataclasses import dataclass, field
from enum import Enum


class Action(str, Enum):
    FOLD = "FOLD"
    HIT = "HIT"
    STAND = "STAND"
    DOUBLE = "DOUBLE"
    CALL = "CALL"
    RAISE = "RAISE"
    CHECK = "CHECK"


@dataclass
class GameState:
    phase: str
    visible_cards: list
    message: str
    extra: dict = field(default_factory=dict)


@dataclass
class RoundResult:
    outcome: str  # "WIN" | "LOSE" | "PUSH" | "FOLD"
    message: str
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/core/test_types.py -v
```
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/types.py tests/core/test_types.py
git commit -m "feat: add core types (Action, GameState, RoundResult)"
```

---

## Task 3: Core Card

**Files:**
- Create: `core/card.py`
- Create: `tests/core/test_card.py`

- [ ] **Step 1: Write failing tests**

Create `tests/core/test_card.py`:
```python
from core.card import Card


def test_repr():
    assert repr(Card('A', 'Hearts')) == "A of Hearts"


def test_value_ace():
    assert Card('A', 'Hearts').value() == 14


def test_value_king():
    assert Card('K', 'Spades').value() == 13


def test_value_queen():
    assert Card('Q', 'Clubs').value() == 12


def test_value_jack():
    assert Card('J', 'Diamonds').value() == 11


def test_value_ten():
    assert Card('10', 'Hearts').value() == 10


def test_value_number():
    assert Card('7', 'Clubs').value() == 7


def test_lt():
    assert Card('2', 'Hearts') < Card('K', 'Spades')


def test_not_lt_higher():
    assert not (Card('K', 'Spades') < Card('2', 'Hearts'))


def test_eq_same_rank_and_suit():
    assert Card('A', 'Hearts') == Card('A', 'Hearts')


def test_eq_different_suit():
    assert Card('A', 'Hearts') != Card('A', 'Spades')


def test_eq_different_rank():
    assert Card('A', 'Hearts') != Card('K', 'Hearts')


def test_hashable():
    s = {Card('A', 'Hearts'), Card('A', 'Hearts'), Card('K', 'Spades')}
    assert len(s) == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_card.py -v
```
Expected: `ModuleNotFoundError: No module named 'core.card'`

- [ ] **Step 3: Implement `core/card.py`**

```python
class Card:
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14,
    }

    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def __repr__(self) -> str:
        return f"{self.rank} of {self.suit}"

    def value(self) -> int:
        return self.RANK_VALUES.get(self.rank, 0)

    def __lt__(self, other: 'Card') -> bool:
        return self.value() < other.value()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/core/test_card.py -v
```
Expected: 13 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/card.py tests/core/test_card.py
git commit -m "feat: add core Card class"
```

---

## Task 4: Core Deck

**Files:**
- Create: `core/deck.py`
- Create: `tests/core/test_deck.py`

- [ ] **Step 1: Write failing tests**

Create `tests/core/test_deck.py`:
```python
from core.card import Card
from core.deck import Deck


def test_default_deck_size():
    assert len(Deck()) == 52


def test_two_decks():
    assert len(Deck(n_decks=2)) == 104


def test_jokers_included():
    d = Deck(include_jokers=True)
    jokers = [c for c in d.cards if c.rank == 'Joker']
    assert len(jokers) == 1


def test_no_jokers_by_default():
    d = Deck()
    assert all(c.rank != 'Joker' for c in d.cards)


def test_draw_returns_card():
    assert isinstance(Deck().draw(), Card)


def test_draw_reduces_size():
    d = Deck()
    d.draw()
    assert len(d) == 51


def test_draw_empty_deck_returns_none():
    d = Deck()
    for _ in range(52):
        d.draw()
    assert d.draw() is None


def test_deck_is_shuffled():
    # Two fresh decks should not be in the same order (astronomically unlikely)
    d1, d2 = Deck(), Deck()
    assert [repr(c) for c in d1.cards] != [repr(c) for c in d2.cards]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_deck.py -v
```
Expected: `ModuleNotFoundError: No module named 'core.deck'`

- [ ] **Step 3: Implement `core/deck.py`**

```python
import random
from core.card import Card

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


class Deck:
    def __init__(self, n_decks: int = 1, include_jokers: bool = False) -> None:
        self.cards = [
            Card(rank, suit)
            for _ in range(n_decks)
            for suit in SUITS
            for rank in RANKS
        ]
        if include_jokers:
            for _ in range(n_decks):
                self.cards.append(Card('Joker', 'Joker'))
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        return self.cards.pop() if self.cards else None

    def __len__(self) -> int:
        return len(self.cards)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/core/test_deck.py -v
```
Expected: 8 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/deck.py tests/core/test_deck.py
git commit -m "feat: add core Deck class with n_decks and include_jokers support"
```

---

## Task 5: Core Player

**Files:**
- Create: `core/player.py`
- Create: `tests/core/test_player.py`

- [ ] **Step 1: Write failing tests**

Create `tests/core/test_player.py`:
```python
from core.card import Card
from core.player import Player


def test_default_name():
    assert Player().name == "Player"


def test_custom_name():
    assert Player("Alice").name == "Alice"


def test_starts_with_empty_hand():
    assert Player().hand == []


def test_receive_card():
    p = Player()
    c = Card('A', 'Hearts')
    p.receive_card(c)
    assert c in p.hand


def test_receive_multiple_cards():
    p = Player()
    p.receive_card(Card('A', 'Hearts'))
    p.receive_card(Card('K', 'Spades'))
    assert len(p.hand) == 2


def test_clear_hand():
    p = Player()
    p.receive_card(Card('A', 'Hearts'))
    p.clear_hand()
    assert p.hand == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_player.py -v
```
Expected: `ModuleNotFoundError: No module named 'core.player'`

- [ ] **Step 3: Implement `core/player.py`**

```python
from core.card import Card


class Player:
    def __init__(self, name: str = "Player") -> None:
        self.name = name
        self.hand: list[Card] = []

    def receive_card(self, card: Card) -> None:
        self.hand.append(card)

    def clear_hand(self) -> None:
        self.hand = []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/core/test_player.py -v
```
Expected: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add core/player.py tests/core/test_player.py
git commit -m "feat: add core Player class"
```

---

## Task 6: BaseGame and GameRegistry

**Files:**
- Create: `core/base_game.py`
- Create: `core/registry.py`
- Create: `tests/core/test_registry.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write failing tests**

Create `tests/conftest.py`:
```python
import pytest
from core.registry import GameRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    saved = dict(GameRegistry._games)
    yield
    GameRegistry._games.clear()
    GameRegistry._games.update(saved)
```

Create `tests/core/test_registry.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/core/test_registry.py -v
```
Expected: `ModuleNotFoundError: No module named 'core.base_game'`

- [ ] **Step 3: Implement `core/base_game.py`**

```python
from abc import ABC, abstractmethod
from core.types import Action, GameState, RoundResult


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

- [ ] **Step 4: Implement `core/registry.py`**

```python
from core.base_game import BaseGame


class GameRegistry:
    _games: dict[str, type[BaseGame]] = {}

    @classmethod
    def register(cls, name: str, game_class: type[BaseGame]) -> None:
        cls._games[name] = game_class

    @classmethod
    def get(cls, name: str) -> BaseGame:
        if name not in cls._games:
            raise KeyError(
                f"Unknown game: '{name}'. Available: {cls.available()}"
            )
        return cls._games[name]()

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._games.keys())
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/core/test_registry.py -v
```
Expected: 5 PASSED

- [ ] **Step 6: Commit**

```bash
git add core/base_game.py core/registry.py tests/core/test_registry.py tests/conftest.py
git commit -m "feat: add BaseGame ABC and GameRegistry"
```

---

## Task 7: Blackjack Rules

**Files:**
- Create: `games/blackjack/rules.py`
- Create: `tests/games/test_blackjack_rules.py`

- [ ] **Step 1: Write failing tests**

Create `tests/games/test_blackjack_rules.py`:
```python
from core.card import Card
from games.blackjack.rules import compare_hands, dealer_should_hit, hand_value, is_bust


def test_hand_value_number_cards():
    assert hand_value([Card('7', 'H'), Card('8', 'C')]) == 15


def test_hand_value_face_cards_are_10():
    assert hand_value([Card('J', 'H'), Card('Q', 'C'), Card('K', 'S')]) == 30


def test_hand_value_ace_as_11():
    assert hand_value([Card('A', 'H'), Card('9', 'C')]) == 20


def test_hand_value_ace_drops_to_1_to_avoid_bust():
    assert hand_value([Card('A', 'H'), Card('9', 'C'), Card('5', 'D')]) == 15


def test_hand_value_blackjack():
    assert hand_value([Card('A', 'H'), Card('K', 'C')]) == 21


def test_hand_value_two_aces():
    # One ace = 11, second ace must = 1 to avoid bust
    assert hand_value([Card('A', 'H'), Card('A', 'D')]) == 12


def test_is_bust_over_21():
    assert is_bust([Card('10', 'H'), Card('Q', 'C'), Card('5', 'D')]) is True


def test_is_bust_exactly_21():
    assert is_bust([Card('A', 'H'), Card('K', 'C')]) is False


def test_is_bust_under_21():
    assert is_bust([Card('10', 'H'), Card('9', 'C')]) is False


def test_dealer_should_hit_at_16():
    assert dealer_should_hit([Card('9', 'H'), Card('7', 'C')]) is True


def test_dealer_should_not_hit_at_17():
    assert dealer_should_hit([Card('10', 'H'), Card('7', 'C')]) is False


def test_dealer_should_not_hit_above_17():
    assert dealer_should_hit([Card('10', 'H'), Card('9', 'C')]) is False


def test_compare_player_wins():
    player = [Card('10', 'H'), Card('9', 'C')]   # 19
    dealer = [Card('10', 'H'), Card('7', 'C')]   # 17
    assert compare_hands(player, dealer) == "WIN"


def test_compare_dealer_wins():
    player = [Card('10', 'H'), Card('7', 'C')]   # 17
    dealer = [Card('10', 'H'), Card('9', 'C')]   # 19
    assert compare_hands(player, dealer) == "LOSE"


def test_compare_push():
    player = [Card('10', 'H'), Card('8', 'C')]   # 18
    dealer = [Card('9', 'H'), Card('9', 'C')]    # 18
    assert compare_hands(player, dealer) == "PUSH"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/games/test_blackjack_rules.py -v
```
Expected: `ModuleNotFoundError: No module named 'games.blackjack.rules'`

- [ ] **Step 3: Implement `games/blackjack/rules.py`**

```python
from core.card import Card


def hand_value(cards: list[Card]) -> int:
    total = 0
    aces = 0
    for card in cards:
        if card.rank in ('J', 'Q', 'K'):
            total += 10
        elif card.rank == 'A':
            aces += 1
            total += 11
        else:
            total += int(card.rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def is_bust(cards: list[Card]) -> bool:
    return hand_value(cards) > 21


def dealer_should_hit(cards: list[Card]) -> bool:
    return hand_value(cards) < 17


def compare_hands(player_cards: list[Card], dealer_cards: list[Card]) -> str:
    player_val = hand_value(player_cards)
    dealer_val = hand_value(dealer_cards)
    if player_val > dealer_val:
        return "WIN"
    if player_val < dealer_val:
        return "LOSE"
    return "PUSH"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/games/test_blackjack_rules.py -v
```
Expected: 15 PASSED

- [ ] **Step 5: Commit**

```bash
git add games/blackjack/rules.py tests/games/test_blackjack_rules.py
git commit -m "feat: add Blackjack rules (hand_value, is_bust, dealer AI, compare)"
```

---

## Task 8: BlackjackGame

**Files:**
- Create: `games/blackjack/game.py`
- Create: `tests/games/test_blackjack_game.py`

- [ ] **Step 1: Write failing tests**

Create `tests/games/test_blackjack_game.py`:
```python
import pytest
from core.card import Card
from core.types import Action
from games.blackjack.game import BlackjackGame
from games.blackjack.rules import hand_value


def test_start_round_phase_is_player_turn():
    game = BlackjackGame()
    state = game.start_round()
    assert state.phase == "PLAYER_TURN"


def test_start_round_deals_two_cards_to_player():
    game = BlackjackGame()
    game.start_round()
    assert len(game._player.hand) == 2


def test_start_round_deals_two_cards_to_dealer():
    game = BlackjackGame()
    game.start_round()
    assert len(game._dealer_hand) == 2


def test_valid_actions_on_fresh_deal_include_double():
    game = BlackjackGame()
    game.start_round()
    actions = game.get_valid_actions()
    assert Action.HIT in actions
    assert Action.STAND in actions
    assert Action.DOUBLE in actions


def test_hit_adds_card_to_player():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.HIT)
    assert len(game._player.hand) == 3


def test_after_hit_double_not_in_valid_actions():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.HIT)
    assert Action.DOUBLE not in game.get_valid_actions()


def test_stand_ends_round():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.is_round_over() is True


def test_stand_result_is_win_lose_or_push():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.get_result().outcome in ("WIN", "LOSE", "PUSH")


def test_bust_on_hit_ends_round_with_lose():
    game = BlackjackGame()
    game.start_round()
    game._player.hand = [Card('10', 'H'), Card('10', 'C')]
    game._phase = "PLAYER_TURN"
    game._deck.cards.append(Card('10', 'D'))  # next draw = bust
    game.apply_action(Action.HIT)
    assert game.is_round_over() is True
    assert game.get_result().outcome == "LOSE"


def test_double_deals_one_card_then_ends():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.DOUBLE)
    assert game.is_round_over() is True
    assert len(game._player.hand) == 3


def test_result_raises_before_round_over():
    game = BlackjackGame()
    game.start_round()
    with pytest.raises(RuntimeError):
        game.get_result()


def test_state_hides_dealer_hole_card_during_player_turn():
    game = BlackjackGame()
    game.start_round()
    state = game._state()
    assert len(state.extra["dealer_visible"]) == 1


def test_state_reveals_full_dealer_hand_after_stand():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    state = game._state()
    assert len(state.extra["dealer_visible"]) == len(game._dealer_hand)


def test_start_round_resets_previous_round():
    game = BlackjackGame()
    game.start_round()
    game.apply_action(Action.STAND)
    assert game.is_round_over() is True
    game.start_round()
    assert game.is_round_over() is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/games/test_blackjack_game.py -v
```
Expected: `ModuleNotFoundError: No module named 'games.blackjack.game'`

- [ ] **Step 3: Implement `games/blackjack/game.py`**

```python
from core.base_game import BaseGame
from core.deck import Deck
from core.player import Player
from core.types import Action, GameState, RoundResult
from games.blackjack.rules import (
    compare_hands,
    dealer_should_hit,
    hand_value,
    is_bust,
)


class BlackjackGame(BaseGame):
    def __init__(self) -> None:
        self._deck = Deck(n_decks=6)
        self._player = Player("Player")
        self._dealer_hand: list = []
        self._phase = "WAITING"
        self._round_over = False
        self._result: RoundResult | None = None

    def start_round(self) -> GameState:
        self._player.clear_hand()
        self._dealer_hand = []
        self._round_over = False
        self._result = None
        self._player.receive_card(self._deck.draw())
        self._dealer_hand.append(self._deck.draw())
        self._player.receive_card(self._deck.draw())
        self._dealer_hand.append(self._deck.draw())
        self._phase = "PLAYER_TURN"
        return self._state()

    def get_valid_actions(self) -> list[Action]:
        if self._phase != "PLAYER_TURN":
            return []
        actions = [Action.HIT, Action.STAND]
        if len(self._player.hand) == 2:
            actions.append(Action.DOUBLE)
        return actions

    def apply_action(self, action: Action) -> GameState:
        if self._phase != "PLAYER_TURN":
            return self._state()
        if action == Action.HIT:
            self._player.receive_card(self._deck.draw())
            if is_bust(self._player.hand):
                self._result = RoundResult(outcome="LOSE", message="Bust! You went over 21.")
                self._phase = "ROUND_OVER"
                self._round_over = True
        elif action == Action.STAND:
            self._run_dealer()
        elif action == Action.DOUBLE:
            self._player.receive_card(self._deck.draw())
            if is_bust(self._player.hand):
                self._result = RoundResult(outcome="LOSE", message="Bust on double!")
                self._phase = "ROUND_OVER"
                self._round_over = True
            else:
                self._run_dealer()
        return self._state()

    def is_round_over(self) -> bool:
        return self._round_over

    def get_result(self) -> RoundResult:
        if self._result is None:
            raise RuntimeError("Round is not over yet.")
        return self._result

    def _run_dealer(self) -> None:
        self._phase = "DEALER_TURN"
        while dealer_should_hit(self._dealer_hand):
            self._dealer_hand.append(self._deck.draw())
        outcome = compare_hands(self._player.hand, self._dealer_hand)
        messages = {"WIN": "You win!", "LOSE": "Dealer wins.", "PUSH": "Push — it's a tie."}
        self._result = RoundResult(outcome=outcome, message=messages[outcome])
        self._phase = "ROUND_OVER"
        self._round_over = True

    def _state(self) -> GameState:
        dealer_visible = (
            self._dealer_hand[:1]
            if self._phase == "PLAYER_TURN"
            else list(self._dealer_hand)
        )
        msg = (
            self._result.message
            if self._result
            else f"Your hand: {hand_value(self._player.hand)}. Dealer shows: {self._dealer_hand[0]}"
        )
        return GameState(
            phase=self._phase,
            visible_cards=list(self._player.hand) + dealer_visible,
            message=msg,
            extra={
                "player_hand": [str(c) for c in self._player.hand],
                "player_value": hand_value(self._player.hand),
                "dealer_visible": [str(c) for c in dealer_visible],
            },
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/games/test_blackjack_game.py -v
```
Expected: 14 PASSED

- [ ] **Step 5: Commit**

```bash
git add games/blackjack/game.py tests/games/test_blackjack_game.py
git commit -m "feat: add BlackjackGame with full round flow"
```

---

## Task 9: Texas Hold'em Rules

**Files:**
- Create: `games/texas_holdem/rules.py`
- Create: `tests/games/test_texas_holdem_rules.py`

This task migrates and enhances the hand evaluation logic from the root-level `game.py`. Key changes: removes Joker support, adds `TWO_PAIR` and `STRAIGHT_FLUSH`, changes Ace to high (14), adds `best_hand` for 7-card evaluation, adds `bot_action` heuristic.

- [ ] **Step 1: Write failing tests**

Create `tests/games/test_texas_holdem_rules.py`:
```python
from core.card import Card
from core.types import Action
from games.texas_holdem.rules import HandRank, bot_action, best_hand, evaluate_hand


# --- evaluate_hand ---

def test_royal_flush():
    cards = [Card('10','H'), Card('J','H'), Card('Q','H'), Card('K','H'), Card('A','H')]
    assert evaluate_hand(cards) == HandRank.ROYAL_FLUSH


def test_straight_flush():
    cards = [Card('5','C'), Card('6','C'), Card('7','C'), Card('8','C'), Card('9','C')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT_FLUSH


def test_four_of_a_kind():
    cards = [Card('A','H'), Card('A','D'), Card('A','C'), Card('A','S'), Card('K','H')]
    assert evaluate_hand(cards) == HandRank.FOUR_OF_A_KIND


def test_full_house():
    cards = [Card('K','H'), Card('K','D'), Card('K','C'), Card('Q','H'), Card('Q','D')]
    assert evaluate_hand(cards) == HandRank.FULL_HOUSE


def test_flush():
    cards = [Card('2','H'), Card('5','H'), Card('9','H'), Card('J','H'), Card('K','H')]
    assert evaluate_hand(cards) == HandRank.FLUSH


def test_straight():
    cards = [Card('5','H'), Card('6','D'), Card('7','C'), Card('8','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT


def test_ace_low_straight():
    cards = [Card('A','H'), Card('2','D'), Card('3','C'), Card('4','S'), Card('5','H')]
    assert evaluate_hand(cards) == HandRank.STRAIGHT


def test_three_of_a_kind():
    cards = [Card('7','H'), Card('7','D'), Card('7','C'), Card('2','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.THREE_OF_A_KIND


def test_two_pair():
    cards = [Card('J','H'), Card('J','D'), Card('9','C'), Card('9','S'), Card('A','H')]
    assert evaluate_hand(cards) == HandRank.TWO_PAIR


def test_pair():
    cards = [Card('A','H'), Card('A','D'), Card('3','C'), Card('7','S'), Card('9','H')]
    assert evaluate_hand(cards) == HandRank.PAIR


def test_high_card():
    cards = [Card('2','H'), Card('5','D'), Card('7','C'), Card('9','S'), Card('J','H')]
    assert evaluate_hand(cards) == HandRank.HIGH_CARD


def test_hand_rank_ordering():
    assert HandRank.HIGH_CARD < HandRank.PAIR < HandRank.TWO_PAIR
    assert HandRank.TWO_PAIR < HandRank.THREE_OF_A_KIND < HandRank.STRAIGHT
    assert HandRank.STRAIGHT < HandRank.FLUSH < HandRank.FULL_HOUSE
    assert HandRank.FULL_HOUSE < HandRank.FOUR_OF_A_KIND < HandRank.STRAIGHT_FLUSH
    assert HandRank.STRAIGHT_FLUSH < HandRank.ROYAL_FLUSH


# --- best_hand ---

def test_best_hand_finds_royal_flush_in_seven_cards():
    cards = [
        Card('10','H'), Card('J','H'), Card('Q','H'), Card('K','H'), Card('A','H'),
        Card('2','D'), Card('3','C'),
    ]
    rank, _ = best_hand(cards)
    assert rank == HandRank.ROYAL_FLUSH


def test_best_hand_returns_five_cards():
    cards = [
        Card('2','H'), Card('5','D'), Card('7','C'), Card('9','S'), Card('J','H'),
        Card('3','D'), Card('4','C'),
    ]
    rank, combo = best_hand(cards)
    assert len(combo) == 5


# --- bot_action pre-flop ---

def test_bot_raises_on_pocket_pair():
    hole = [Card('A','H'), Card('A','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.RAISE


def test_bot_raises_on_ace_high():
    hole = [Card('A','H'), Card('7','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.RAISE


def test_bot_calls_on_medium_cards():
    hole = [Card('9','H'), Card('8','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.CALL


def test_bot_folds_weak_pre_flop():
    hole = [Card('2','H'), Card('7','D')]
    assert bot_action(hole, [], "PRE_FLOP") == Action.FOLD


# --- bot_action post-flop ---

def test_bot_raises_strong_post_flop():
    hole = [Card('A','H'), Card('A','D')]
    community = [Card('A','C'), Card('K','S'), Card('2','H')]
    assert bot_action(hole, community, "FLOP") == Action.RAISE


def test_bot_calls_pair_post_flop():
    hole = [Card('9','H'), Card('3','D')]
    community = [Card('9','C'), Card('2','S'), Card('7','H')]
    assert bot_action(hole, community, "FLOP") == Action.CALL


def test_bot_folds_weak_post_flop():
    hole = [Card('2','H'), Card('7','D')]
    community = [Card('A','C'), Card('K','S'), Card('Q','H')]
    assert bot_action(hole, community, "FLOP") == Action.FOLD
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/games/test_texas_holdem_rules.py -v
```
Expected: `ModuleNotFoundError: No module named 'games.texas_holdem.rules'`

- [ ] **Step 3: Implement `games/texas_holdem/rules.py`**

```python
from collections import defaultdict
from enum import IntEnum
from itertools import combinations

from core.card import Card
from core.types import Action


class HandRank(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


def _rank_counts(cards: list[Card]) -> list[int]:
    counts: dict[str, int] = defaultdict(int)
    for card in cards:
        counts[card.rank] += 1
    return sorted(counts.values(), reverse=True)


def _is_flush(cards: list[Card]) -> bool:
    return len({card.suit for card in cards}) == 1


def _is_straight(cards: list[Card]) -> bool:
    values = sorted({card.value() for card in cards})
    if len(values) != 5:
        return False
    if values[-1] - values[0] == 4:
        return True
    return values == [2, 3, 4, 5, 14]  # ace-low


def evaluate_hand(cards: list[Card]) -> HandRank:
    freq = _rank_counts(cards)
    flush = _is_flush(cards)
    straight = _is_straight(cards)

    if flush and straight:
        if sorted(c.value() for c in cards) == [10, 11, 12, 13, 14]:
            return HandRank.ROYAL_FLUSH
        return HandRank.STRAIGHT_FLUSH
    if freq[0] == 4:
        return HandRank.FOUR_OF_A_KIND
    if freq[0] == 3 and freq[1] == 2:
        return HandRank.FULL_HOUSE
    if flush:
        return HandRank.FLUSH
    if straight:
        return HandRank.STRAIGHT
    if freq[0] == 3:
        return HandRank.THREE_OF_A_KIND
    if freq[0] == 2 and freq[1] == 2:
        return HandRank.TWO_PAIR
    if freq[0] == 2:
        return HandRank.PAIR
    return HandRank.HIGH_CARD


def best_hand(cards: list[Card]) -> tuple[HandRank, list[Card]]:
    best_rank = HandRank.HIGH_CARD
    best_combo: list[Card] = list(cards[:5])
    for combo in combinations(cards, 5):
        rank = evaluate_hand(list(combo))
        if rank > best_rank:
            best_rank = rank
            best_combo = list(combo)
    return best_rank, best_combo


def bot_action(
    hole_cards: list[Card], community_cards: list[Card], phase: str
) -> Action:
    if phase == "PRE_FLOP":
        ranks = {c.rank for c in hole_cards}
        is_pair = len({c.rank for c in hole_cards}) == 1
        high_ranks = {'A', 'K', 'Q'}
        if is_pair or any(r in high_ranks for r in ranks):
            return Action.RAISE
        if max(c.value() for c in hole_cards) >= 9:
            return Action.CALL
        return Action.FOLD

    rank, _ = best_hand(hole_cards + community_cards)
    if rank >= HandRank.THREE_OF_A_KIND:
        return Action.RAISE
    if rank >= HandRank.PAIR:
        return Action.CALL
    return Action.FOLD
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/games/test_texas_holdem_rules.py -v
```
Expected: 21 PASSED

- [ ] **Step 5: Commit**

```bash
git add games/texas_holdem/rules.py tests/games/test_texas_holdem_rules.py
git commit -m "feat: add Texas Hold'em rules (HandRank, evaluate_hand, best_hand, bot_action)"
```

---

## Task 10: TexasHoldemGame

**Files:**
- Create: `games/texas_holdem/game.py`
- Create: `tests/games/test_texas_holdem_game.py`

- [ ] **Step 1: Write failing tests**

Create `tests/games/test_texas_holdem_game.py`:
```python
import pytest
from core.card import Card
from core.types import Action
from games.texas_holdem.game import TexasHoldemGame


def test_start_round_phase_is_pre_flop():
    game = TexasHoldemGame()
    state = game.start_round()
    assert state.phase == "PRE_FLOP"


def test_start_round_deals_two_hole_cards_each():
    game = TexasHoldemGame()
    game.start_round()
    assert len(game._player.hand) == 2
    assert len(game._bot.hand) == 2


def test_no_community_cards_at_start():
    game = TexasHoldemGame()
    game.start_round()
    assert game._community == []


def test_pre_flop_valid_actions():
    game = TexasHoldemGame()
    game.start_round()
    actions = game.get_valid_actions()
    assert Action.FOLD in actions
    assert Action.CALL in actions
    assert Action.RAISE in actions


def test_fold_ends_round_immediately():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.is_round_over() is True


def test_fold_result_is_fold():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.get_result().outcome == "FOLD"


def test_call_pre_flop_advances_to_flop_or_ends():
    game = TexasHoldemGame()
    game.start_round()
    # Give bot strong cards so it won't fold
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    state = game.apply_action(Action.CALL)
    assert state.phase in ("FLOP", "ROUND_OVER")


def test_flop_deals_three_community_cards():
    game = TexasHoldemGame()
    game.start_round()
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    game.apply_action(Action.CALL)
    if not game.is_round_over():
        assert len(game._community) == 3


def test_full_round_reaches_valid_result():
    game = TexasHoldemGame()
    game.start_round()
    # Give bot a pair so it won't fold at any phase
    game._bot.hand = [Card('A', 'C'), Card('A', 'S')]
    while not game.is_round_over():
        actions = game.get_valid_actions()
        action = Action.CHECK if Action.CHECK in actions else Action.CALL
        game.apply_action(action)
    assert game.get_result().outcome in ("WIN", "LOSE", "PUSH")


def test_result_raises_before_round_over():
    game = TexasHoldemGame()
    game.start_round()
    with pytest.raises(RuntimeError):
        game.get_result()


def test_start_round_resets_state():
    game = TexasHoldemGame()
    game.start_round()
    game.apply_action(Action.FOLD)
    assert game.is_round_over() is True
    game.start_round()
    assert game.is_round_over() is False
    assert game._community == []


def test_state_extra_contains_player_hand_and_community():
    game = TexasHoldemGame()
    state = game.start_round()
    assert "player_hand" in state.extra
    assert "community_cards" in state.extra
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/games/test_texas_holdem_game.py -v
```
Expected: `ModuleNotFoundError: No module named 'games.texas_holdem.game'`

- [ ] **Step 3: Implement `games/texas_holdem/game.py`**

```python
from core.base_game import BaseGame
from core.deck import Deck
from core.player import Player
from core.types import Action, GameState, RoundResult
from games.texas_holdem.rules import best_hand, bot_action


class TexasHoldemGame(BaseGame):
    def __init__(self) -> None:
        self._player = Player("Player")
        self._bot = Player("Bot")
        self._deck = Deck()
        self._community: list = []
        self._phase = "WAITING"
        self._round_over = False
        self._result: RoundResult | None = None

    def start_round(self) -> GameState:
        self._deck = Deck()
        self._player.clear_hand()
        self._bot.clear_hand()
        self._community = []
        self._round_over = False
        self._result = None
        for _ in range(2):
            self._player.receive_card(self._deck.draw())
            self._bot.receive_card(self._deck.draw())
        self._phase = "PRE_FLOP"
        return self._state()

    def get_valid_actions(self) -> list[Action]:
        if self._round_over:
            return []
        if self._phase == "PRE_FLOP":
            return [Action.FOLD, Action.CALL, Action.RAISE]
        return [Action.FOLD, Action.CHECK, Action.CALL, Action.RAISE]

    def apply_action(self, action: Action) -> GameState:
        if self._round_over:
            return self._state()

        if action == Action.FOLD:
            self._result = RoundResult(outcome="FOLD", message="You folded. Bot wins.")
            self._phase = "ROUND_OVER"
            self._round_over = True
            return self._state()

        bot_act = bot_action(self._bot.hand, self._community, self._phase)
        if bot_act == Action.FOLD:
            self._result = RoundResult(outcome="WIN", message="Bot folded. You win!")
            self._phase = "ROUND_OVER"
            self._round_over = True
            return self._state()

        self._advance_phase()
        return self._state()

    def is_round_over(self) -> bool:
        return self._round_over

    def get_result(self) -> RoundResult:
        if self._result is None:
            raise RuntimeError("Round is not over yet.")
        return self._result

    def _advance_phase(self) -> None:
        if self._phase == "PRE_FLOP":
            for _ in range(3):
                self._community.append(self._deck.draw())
            self._phase = "FLOP"
        elif self._phase == "FLOP":
            self._community.append(self._deck.draw())
            self._phase = "TURN"
        elif self._phase == "TURN":
            self._community.append(self._deck.draw())
            self._phase = "RIVER"
        elif self._phase == "RIVER":
            self._resolve_showdown()

    def _resolve_showdown(self) -> None:
        self._phase = "SHOWDOWN"
        player_rank, _ = best_hand(self._player.hand + self._community)
        bot_rank, _ = best_hand(self._bot.hand + self._community)
        if player_rank > bot_rank:
            name = player_rank.name.replace('_', ' ').title()
            self._result = RoundResult(outcome="WIN", message=f"You win with {name}!")
        elif bot_rank > player_rank:
            name = bot_rank.name.replace('_', ' ').title()
            self._result = RoundResult(outcome="LOSE", message=f"Bot wins with {name}.")
        else:
            self._result = RoundResult(outcome="PUSH", message="Split pot — tie!")
        self._round_over = True
        self._phase = "ROUND_OVER"

    def _state(self) -> GameState:
        msg = (
            self._result.message
            if self._result
            else f"Phase: {self._phase}. Community: {self._community or 'none'}"
        )
        return GameState(
            phase=self._phase,
            visible_cards=list(self._player.hand) + list(self._community),
            message=msg,
            extra={
                "player_hand": [str(c) for c in self._player.hand],
                "community_cards": [str(c) for c in self._community],
                "phase": self._phase,
            },
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/games/test_texas_holdem_game.py -v
```
Expected: 12 PASSED

- [ ] **Step 5: Commit**

```bash
git add games/texas_holdem/game.py tests/games/test_texas_holdem_game.py
git commit -m "feat: add TexasHoldemGame with full phase flow and showdown"
```

---

## Task 11: Registration, main.py, and Cleanup

**Files:**
- Modify: `games/blackjack/__init__.py`
- Modify: `games/texas_holdem/__init__.py`
- Rewrite: `main.py`
- Delete: `card.py`, `deck.py`, `player.py`, `game.py`

- [ ] **Step 1: Add self-registration to `games/blackjack/__init__.py`**

```python
from core.registry import GameRegistry
from games.blackjack.game import BlackjackGame

GameRegistry.register("blackjack", BlackjackGame)
```

- [ ] **Step 2: Add self-registration to `games/texas_holdem/__init__.py`**

```python
from core.registry import GameRegistry
from games.texas_holdem.game import TexasHoldemGame

GameRegistry.register("texas_holdem", TexasHoldemGame)
```

- [ ] **Step 3: Write integration test**

Create `tests/test_integration.py`:
```python
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
```

- [ ] **Step 4: Run integration test**

```bash
pytest tests/test_integration.py -v
```
Expected: 3 PASSED

- [ ] **Step 5: Rewrite `main.py`**

```python
import games.blackjack  # noqa: F401 — triggers registration
import games.texas_holdem  # noqa: F401 — triggers registration

from core.registry import GameRegistry
from core.types import Action


def main() -> None:
    available = GameRegistry.available()
    print(f"Available games: {', '.join(available)}")
    name = input("Select a game: ").strip().lower()
    try:
        game = GameRegistry.get(name)
    except KeyError as e:
        print(e)
        return

    print(f"\nStarting {name}...\n")
    state = game.start_round()
    print(state.message)

    while not game.is_round_over():
        actions = game.get_valid_actions()
        print(f"Actions: {[a.value for a in actions]}")
        raw = input("Your action: ").strip().upper()
        try:
            action = Action(raw)
        except ValueError:
            print(f"Invalid. Choose from: {[a.value for a in actions]}")
            continue
        if action not in actions:
            print(f"Not valid here. Choose from: {[a.value for a in actions]}")
            continue
        state = game.apply_action(action)
        print(state.message)

    result = game.get_result()
    print(f"\nResult: {result.outcome} — {result.message}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Delete old root-level files**

```bash
rm card.py deck.py player.py game.py
```

- [ ] **Step 7: Run full test suite**

```bash
pytest -v
```
Expected: all tests PASSED, none referencing old files

- [ ] **Step 8: Smoke-test the runner**

```bash
python main.py
```
Expected: Prompts for game selection, then plays a round.

- [ ] **Step 9: Commit**

```bash
git add games/blackjack/__init__.py games/texas_holdem/__init__.py main.py tests/test_integration.py
git rm card.py deck.py player.py game.py
git commit -m "feat: wire game registry, rewrite runner, remove legacy files"
```

---

## Verification

Run the full test suite:
```bash
pytest -v
```
Expected: all tests pass across `tests/core/`, `tests/games/`, and `tests/`.

Smoke-test the CLI:
```bash
python main.py
# Select: blackjack → play HIT/STAND/DOUBLE until round over
# Select: texas_holdem → play CALL/CHECK/RAISE/FOLD until round over
```

Verify JSON-readiness:
```python
import dataclasses, games.blackjack
from core.registry import GameRegistry
from core.types import Action

game = GameRegistry.get("blackjack")
state = game.start_round()
print(dataclasses.asdict(state))   # should print clean dict with no Card objects
```
Note: `visible_cards` contains `Card` objects — the web layer will call `str(c)` or add a `to_dict()` method on `Card` when building the API. `extra` is already fully serializable.
