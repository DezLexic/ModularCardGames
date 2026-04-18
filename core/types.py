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
