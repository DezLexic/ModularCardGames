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
