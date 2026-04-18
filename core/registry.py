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
