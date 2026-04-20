import pytest
import games.blackjack  # noqa: F401
import games.texas_holdem  # noqa: F401

from fastapi.testclient import TestClient

from api.main import app, _store, limiter


@pytest.fixture(autouse=True)
def clear_store():
    _store._sessions.clear()
    limiter._storage.reset()
    yield
    _store._sessions.clear()
    limiter._storage.reset()


@pytest.fixture
def client():
    return TestClient(app)


# ── GET /games ────────────────────────────────────────────────────────────────

class TestGetGames:
    def test_returns_200(self, client):
        resp = client.get("/games")
        assert resp.status_code == 200

    def test_returns_available_games(self, client):
        resp = client.get("/games")
        data = resp.json()
        assert "games" in data
        assert "blackjack" in data["games"]
        assert "texas_holdem" in data["games"]


# ── POST /sessions ────────────────────────────────────────────────────────────

class TestCreateSession:
    def test_returns_201(self, client):
        resp = client.post("/sessions", json={"game": "blackjack"})
        assert resp.status_code == 201

    def test_response_has_session_id_and_state(self, client):
        resp = client.post("/sessions", json={"game": "blackjack"})
        data = resp.json()
        assert "session_id" in data
        assert "state" in data
        assert data["state"]["phase"] == "PLAYER_TURN"

    def test_unknown_game_returns_400(self, client):
        resp = client.post("/sessions", json={"game": "no_such_game"})
        assert resp.status_code == 400

    def test_state_has_required_fields(self, client):
        resp = client.post("/sessions", json={"game": "blackjack"})
        state = resp.json()["state"]
        assert "phase" in state
        assert "visible_cards" in state
        assert "message" in state
        assert "valid_actions" in state
        assert "is_round_over" in state
        assert "result" in state


# ── GET /sessions/{id} ────────────────────────────────────────────────────────

class TestGetSession:
    def test_returns_200_for_existing_session(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.get(f"/sessions/{session_id}")
        assert resp.status_code == 200

    def test_returns_cached_state(self, client):
        create_resp = client.post("/sessions", json={"game": "blackjack"})
        session_id = create_resp.json()["session_id"]
        get_resp = client.get(f"/sessions/{session_id}")
        assert get_resp.json()["phase"] == create_resp.json()["state"]["phase"]

    def test_returns_404_for_unknown_id(self, client):
        resp = client.get("/sessions/nonexistent-id")
        assert resp.status_code == 404


# ── POST /sessions/{id}/action ────────────────────────────────────────────────

class TestApplyAction:
    def test_returns_200_for_valid_action(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "HIT"})
        assert resp.status_code == 200

    def test_response_has_state_fields(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "STAND"})
        data = resp.json()
        assert "phase" in data
        assert "valid_actions" in data
        assert "is_round_over" in data

    def test_stand_leads_to_round_over(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "STAND"})
        assert resp.json()["is_round_over"] is True

    def test_invalid_action_string_returns_400(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "NOT_AN_ACTION"})
        assert resp.status_code == 400

    def test_wrong_phase_action_returns_400(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "CALL"})
        assert resp.status_code == 400

    def test_unknown_session_returns_404(self, client):
        resp = client.post("/sessions/nonexistent-id/action", json={"action": "HIT"})
        assert resp.status_code == 404

    def test_stand_result_has_outcome(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "STAND"})
        data = resp.json()
        assert data["is_round_over"] is True
        assert data["result"] is not None
        assert data["result"]["outcome"] in ("WIN", "LOSE", "PUSH")


# ── DELETE /sessions/{id} ─────────────────────────────────────────────────────

class TestDeleteSession:
    def test_returns_204(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        resp = client.delete(f"/sessions/{session_id}")
        assert resp.status_code == 204

    def test_session_gone_after_delete(self, client):
        session_id = client.post("/sessions", json={"game": "blackjack"}).json()["session_id"]
        client.delete(f"/sessions/{session_id}")
        resp = client.get(f"/sessions/{session_id}")
        assert resp.status_code == 404

    def test_delete_unknown_id_returns_404(self, client):
        resp = client.delete("/sessions/nonexistent-id")
        assert resp.status_code == 404


# ── Texas Hold'em smoke tests ─────────────────────────────────────────────────

class TestTexasHoldem:
    def test_create_holdem_session(self, client):
        resp = client.post("/sessions", json={"game": "texas_holdem"})
        assert resp.status_code == 201
        assert resp.json()["state"]["phase"] == "PRE_FLOP"

    def test_fold_ends_round(self, client):
        session_id = client.post("/sessions", json={"game": "texas_holdem"}).json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/action", json={"action": "FOLD"})
        assert resp.json()["is_round_over"] is True
        assert resp.json()["result"]["outcome"] == "FOLD"


class TestCORS:
    def test_cors_header_present_for_allowed_origin(self, client):
        resp = client.get("/games", headers={"Origin": "http://localhost:3000"})
        assert resp.headers.get("access-control-allow-origin") in (
            "http://localhost:3000", "*"
        )

    def test_preflight_returns_200(self, client):
        resp = client.options(
            "/sessions",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code == 200


class TestSessionCap:
    def test_create_returns_503_when_cap_reached(self, client):
        from api.main import _store
        original_max = _store.MAX_SESSIONS
        _store.MAX_SESSIONS = 1
        client.post("/sessions", json={"game": "blackjack"})
        resp = client.post("/sessions", json={"game": "blackjack"})
        assert resp.status_code == 503
        _store.MAX_SESSIONS = original_max
