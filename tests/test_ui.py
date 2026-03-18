"""
TDD tests for Phase 3 — Terminal UI.

Tests cover display_card, display_feedback, display_stats, get_user_answer,
and exit/interrupt handling.  All tests are written against stub implementations
that raise NotImplementedError; they are expected to FAIL until the
implementations are written (red phase of red-green-refactor).

Run with:
    python3 -m pytest tests/test_ui.py -v --no-header --tb=short
"""
from __future__ import annotations

from unittest.mock import Mock

import pytest

from data_loader import FlashCard
from quiz_engine import SessionStats
from ui import (
    display_card,
    display_feedback,
    display_stats,
    get_user_answer,
)


# ---------------------------------------------------------------------------
# display_card tests
# ---------------------------------------------------------------------------


class TestDisplayCard:
    """display_card() must print the front of the card to stdout."""

    def test_display_card_outputs_front(self, capsys, sample_deck):
        """The card's front text appears somewhere in stdout after display_card."""
        card = sample_deck[0]

        display_card(card)

        captured = capsys.readouterr()
        assert card.front in captured.out


# ---------------------------------------------------------------------------
# display_feedback tests
# ---------------------------------------------------------------------------


class TestDisplayFeedback:
    """display_feedback() prints correctness and, when wrong, the expected answer."""

    def test_display_feedback_correct(self, capsys):
        """Stdout contains 'Correct', 'correct', or a checkmark for a right answer."""
        display_feedback(True, "answer")

        captured = capsys.readouterr()
        output_lower = captured.out.lower()
        assert "correct" in output_lower or "\u2713" in captured.out or "\u2714" in captured.out

    def test_display_feedback_incorrect(self, capsys):
        """Stdout contains 'incorrect' and the expected answer for a wrong answer."""
        expected = "expected answer"

        display_feedback(False, expected)

        captured = capsys.readouterr()
        assert "incorrect" in captured.out.lower()
        assert expected in captured.out


# ---------------------------------------------------------------------------
# display_stats tests
# ---------------------------------------------------------------------------


class TestDisplayStats:
    """display_stats() must surface all key numeric fields in stdout."""

    def test_display_stats_shows_all_fields(self, capsys):
        """total, correct, incorrect, and accuracy all appear in the output."""
        stats = SessionStats(
            total=10,
            correct=8,
            incorrect=2,
            missed_cards=[FlashCard("Q", "A")],
        )

        display_stats(stats)

        captured = capsys.readouterr()
        assert "10" in captured.out
        assert "8" in captured.out
        assert "2" in captured.out
        assert "80.0" in captured.out


# ---------------------------------------------------------------------------
# get_user_answer tests
# ---------------------------------------------------------------------------


class TestGetUserAnswer:
    """get_user_answer() strips whitespace, handles 'exit', and handles Ctrl+C."""

    def test_get_user_answer_strips_whitespace(self, monkeypatch):
        """Surrounding whitespace is removed before returning the user's answer."""
        monkeypatch.setattr("builtins.input", lambda _: "  hello  ")

        result = get_user_answer()

        assert result == "hello"

    def test_exit_command_raises_system_exit(self, monkeypatch):
        """Typing 'exit' causes SystemExit with code 0."""
        monkeypatch.setattr("builtins.input", lambda _: "exit")

        with pytest.raises(SystemExit) as exc_info:
            get_user_answer()

        assert exc_info.value.code == 0

    def test_keyboard_interrupt_raises_system_exit(self, monkeypatch):
        """Pressing Ctrl+C (KeyboardInterrupt) causes SystemExit with code 0."""
        monkeypatch.setattr("builtins.input", Mock(side_effect=KeyboardInterrupt))

        with pytest.raises(SystemExit) as exc_info:
            get_user_answer()

        assert exc_info.value.code == 0

    def test_eof_raises_system_exit(self, monkeypatch):
        """Regression: EOF (Ctrl+D / piped stdin) causes SystemExit with code 0."""
        monkeypatch.setattr("builtins.input", Mock(side_effect=EOFError))

        with pytest.raises(SystemExit) as exc_info:
            get_user_answer()

        assert exc_info.value.code == 0
