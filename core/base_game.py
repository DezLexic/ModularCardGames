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
