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
