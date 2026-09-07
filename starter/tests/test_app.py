"""Tests for Flask API routes."""

import pytest

from app import CURRENT, app


@pytest.fixture(autouse=True)
def reset_game_state():
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None
    CURRENT["difficulty"] = "medium"
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sudoku" in response.data


def test_new_game_returns_puzzle(client):
    response = client.get("/new?difficulty=medium")
    data = response.get_json()

    assert response.status_code == 200
    assert data["difficulty"] == "medium"
    assert len(data["puzzle"]) == 9
    assert all(len(row) == 9 for row in data["puzzle"])
    assert data["clues"] > 0


def test_new_game_rejects_invalid_difficulty(client):
    response = client.get("/new?difficulty=impossible")
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_check_requires_active_game(client):
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_check_and_hint_after_new_game(client):
    new_response = client.get("/new?difficulty=easy")
    puzzle = new_response.get_json()["puzzle"]

    check_response = client.post("/check", json={"board": puzzle})
    check_data = check_response.get_json()

    assert check_response.status_code == 200
    assert check_data["incorrect"] == []
    assert check_data["complete"] is False

    hint_response = client.post("/hint", json={"board": puzzle})
    hint_data = hint_response.get_json()

    assert hint_response.status_code == 200
    assert len(hint_data["hint"]) == 3


def test_conflicts_endpoint_returns_duplicate_positions(client):
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[0][3] = 5

    response = client.post("/conflicts", json={"board": board})
    data = response.get_json()

    assert response.status_code == 200
    assert [0, 0] in data["conflicts"]
    assert [0, 3] in data["conflicts"]


def test_check_requires_board_payload(client):
    client.get("/new?difficulty=medium")
    response = client.post("/check", json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data
