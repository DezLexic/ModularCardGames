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
