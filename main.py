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
