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
