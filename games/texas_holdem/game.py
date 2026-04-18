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
