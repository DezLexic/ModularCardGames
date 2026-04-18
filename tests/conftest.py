import pytest
from core.registry import GameRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    saved = dict(GameRegistry._games)
    yield
    GameRegistry._games.clear()
    GameRegistry._games.update(saved)
