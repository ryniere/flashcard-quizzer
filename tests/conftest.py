"""
Shared pytest fixtures for the Flashcard Quizzer test suite.

Provides reusable FlashCard decks and temporary JSON file fixtures
that cover the full range of valid and invalid input scenarios.
"""
from __future__ import annotations

import json

import pytest

from data_loader import FlashCard


# ---------------------------------------------------------------------------
# Path validation relaxation for tmp_path-based fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def allow_tmp_paths(monkeypatch):
    """Relax SAFE_BASE_DIR so tests can read from pytest's tmp_path.

    Apply via @pytest.mark.usefixtures("allow_tmp_paths") on test classes
    that need to load files from temporary directories. Do NOT apply to
    path traversal tests, which need the real SAFE_BASE_DIR.
    """
    monkeypatch.setattr("utils.file_handler.SAFE_BASE_DIR", "/")


# ---------------------------------------------------------------------------
# In-memory deck fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_deck() -> list[FlashCard]:
    """Return a three-card deck covering typical flashcard content."""
    return [
        FlashCard(front="What is Python?", back="A programming language"),
        FlashCard(front="What is a list?", back="A mutable sequence"),
        FlashCard(front="What is a dict?", back="A key-value mapping"),
    ]


@pytest.fixture
def single_card_deck() -> list[FlashCard]:
    """Return the smallest valid deck: exactly one card."""
    return [FlashCard(front="Q", back="A")]


# ---------------------------------------------------------------------------
# Temporary JSON file fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_array_json(tmp_path):
    """Write a well-formed JSON file using the top-level array format.

    Format: [ {"front": "...", "back": "..."}, ... ]
    """
    cards = [
        {"front": "What is Python?", "back": "A programming language"},
        {"front": "What is a list?", "back": "A mutable sequence"},
        {"front": "What is a dict?", "back": "A key-value mapping"},
    ]
    filepath = tmp_path / "valid_array.json"
    filepath.write_text(json.dumps(cards), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def valid_object_json(tmp_path):
    """Write a well-formed JSON file using the wrapped object format.

    Format: { "cards": [ {"front": "...", "back": "..."}, ... ] }
    """
    payload = {
        "cards": [
            {"front": "What is Python?", "back": "A programming language"},
            {"front": "What is a list?", "back": "A mutable sequence"},
        ]
    }
    filepath = tmp_path / "valid_object.json"
    filepath.write_text(json.dumps(payload), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def invalid_json(tmp_path):
    """Write a file whose contents are not valid JSON."""
    filepath = tmp_path / "invalid.json"
    filepath.write_text("{this is not: valid json,,}", encoding="utf-8")
    return str(filepath)


@pytest.fixture
def missing_back_json(tmp_path):
    """Write a JSON file containing a card that omits the 'back' field."""
    cards = [
        {"front": "What is Python?"},  # 'back' intentionally absent
    ]
    filepath = tmp_path / "missing_back.json"
    filepath.write_text(json.dumps(cards), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def missing_front_json(tmp_path):
    """Write a JSON file containing a card that omits the 'front' field."""
    cards = [
        {"back": "A programming language"},  # 'front' intentionally absent
    ]
    filepath = tmp_path / "missing_front.json"
    filepath.write_text(json.dumps(cards), encoding="utf-8")
    return str(filepath)


@pytest.fixture
def empty_deck_json(tmp_path):
    """Write a JSON file whose card list is an empty array."""
    filepath = tmp_path / "empty_deck.json"
    filepath.write_text(json.dumps([]), encoding="utf-8")
    return str(filepath)
