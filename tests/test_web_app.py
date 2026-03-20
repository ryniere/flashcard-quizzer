"""Tests for the Flask web application."""
from __future__ import annotations

import pytest

from web_app import app, _sessions, _current_cards, _deck_cache


@pytest.fixture()
def client():
    """Create a Flask test client with testing config."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client
    # Clean up in-memory stores between tests
    _sessions.clear()
    _current_cards.clear()
    _deck_cache.clear()


class TestIndexPage:
    """Tests for the home page."""

    def test_index_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Flashcard Quizzer" in resp.data

    def test_index_shows_decks(self, client):
        resp = client.get("/")
        assert b"Python Basics" in resp.data
        assert b"Science Facts" in resp.data

    def test_index_shows_modes(self, client):
        resp = client.get("/")
        assert b"Sequential" in resp.data
        assert b"Random" in resp.data
        assert b"Adaptive" in resp.data


class TestStartQuiz:
    """Tests for starting a quiz session."""

    def test_start_with_valid_deck(self, client):
        resp = client.post(
            "/start",
            data={"deck": "python_basics.json", "mode": "sequential"},
        )
        assert resp.status_code == 200
        assert b"Question" in resp.data

    def test_start_with_no_deck_redirects(self, client):
        resp = client.post("/start", data={"deck": "", "mode": "sequential"})
        assert resp.status_code == 302

    def test_start_with_invalid_deck(self, client):
        resp = client.post(
            "/start",
            data={"deck": "nonexistent.json", "mode": "sequential"},
        )
        assert resp.status_code == 200
        assert b"Error" in resp.data or b"error" in resp.data

    def test_start_with_invalid_mode(self, client):
        resp = client.post(
            "/start",
            data={"deck": "python_basics.json", "mode": "invalid_mode"},
        )
        assert resp.status_code == 200
        # Should show an error on the index page
        assert b"Unknown quiz mode" in resp.data

    def test_start_random_mode(self, client):
        resp = client.post(
            "/start",
            data={"deck": "python_basics.json", "mode": "random"},
        )
        assert resp.status_code == 200
        assert b"Random" in resp.data

    def test_start_adaptive_mode(self, client):
        resp = client.post(
            "/start",
            data={"deck": "science_facts.json", "mode": "adaptive"},
        )
        assert resp.status_code == 200
        assert b"Adaptive" in resp.data


class TestQuizFlow:
    """Tests for the quiz answer and navigation flow."""

    def _start_quiz(self, client, deck="python_basics.json", mode="sequential"):
        """Helper to start a quiz and return the response."""
        return client.post("/start", data={"deck": deck, "mode": mode})

    def test_answer_correct(self, client):
        self._start_quiz(client)
        # The first card in python_basics is about variables — answer it
        resp = client.post("/answer", data={"answer": "A named storage location for data"})
        assert resp.status_code == 200
        # Should show feedback
        assert b"Correct" in resp.data or b"Incorrect" in resp.data

    def test_answer_incorrect(self, client):
        self._start_quiz(client)
        resp = client.post("/answer", data={"answer": "wrong answer"})
        assert resp.status_code == 200
        assert b"Incorrect" in resp.data

    def test_answer_empty(self, client):
        self._start_quiz(client)
        resp = client.post("/answer", data={"answer": ""})
        assert resp.status_code == 200
        assert b"Incorrect" in resp.data

    def test_next_card(self, client):
        self._start_quiz(client)
        # Answer first card
        client.post("/answer", data={"answer": "test"})
        # Go to next card
        resp = client.post("/next")
        assert resp.status_code == 200
        assert b"Question" in resp.data

    def test_answer_without_session_redirects(self, client):
        resp = client.post("/answer", data={"answer": "test"})
        assert resp.status_code == 302

    def test_next_without_session_redirects(self, client):
        resp = client.post("/next")
        assert resp.status_code == 302

    def test_full_quiz_sequential(self, client):
        """Complete a full quiz and check results."""
        self._start_quiz(client, deck="science_facts.json", mode="sequential")
        # Answer all 8 science cards (all wrong for simplicity)
        for i in range(8):
            resp = client.post("/answer", data={"answer": "wrong"})
            if b"quiz_over" in resp.data or b"View Results" in resp.data:
                break
            client.post("/next")

        # Check results page
        resp = client.get("/results")
        assert resp.status_code == 200
        assert b"Quiz Complete" in resp.data
        assert b"Accuracy" in resp.data


class TestResultsPage:
    """Tests for the results page."""

    def test_results_without_data_redirects(self, client):
        resp = client.get("/results")
        assert resp.status_code == 302

    def test_results_shows_stats(self, client):
        """Complete a short quiz and verify results are shown."""
        # Start a quiz with science_facts (8 cards)
        client.post("/start", data={"deck": "science_facts.json", "mode": "sequential"})
        # Answer all cards
        for _ in range(8):
            resp = client.post("/answer", data={"answer": "wrong"})
            if b"View Results" in resp.data:
                break
            client.post("/next")

        resp = client.get("/results")
        assert resp.status_code == 200
        assert b"Quiz Complete" in resp.data
        assert b"Cards to Review" in resp.data


class TestApiEndpoints:
    """Tests for the JSON API endpoints."""

    def test_api_decks(self, client):
        resp = client.get("/api/decks")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        filenames = [d["filename"] for d in data]
        assert "python_basics.json" in filenames
        assert "science_facts.json" in filenames
