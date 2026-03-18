"""
Edge case and hardening tests for the Flashcard Quizzer.

These tests exercise boundary conditions, stress scenarios, and remaining
coverage gaps: extra JSON fields, single-card decks, adaptive exhaustion,
zero-question stats, Unicode answers, paths with spaces, concurrent sessions,
unsupported JSON format, commonpath ValueError, and TOCTOU file disappearance.

Run with:
    python3 -m pytest tests/test_edge_cases.py -v --no-header --tb=short
"""
from __future__ import annotations

import json
import pathlib
from unittest.mock import patch

import pytest

from data_loader import FlashCard, load_flashcards
from main import run
from quiz_engine import (
    AdaptiveMode,
    QuizSession,
    SequentialMode,
    SessionStats,
)
from utils.file_handler import _validate_path


# ---------------------------------------------------------------------------
# Test 1 — Extra JSON fields are silently accepted
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestLoadJsonWithExtraFields:
    """load_flashcards must ignore unknown keys beyond 'front' and 'back'."""

    def test_load_json_with_extra_fields_is_accepted(
        self, tmp_path: pathlib.Path,
    ) -> None:
        """Cards with bonus keys like 'hint' and 'difficulty' load fine."""
        cards_data = [
            {"front": "Q1", "back": "A1", "hint": "think", "difficulty": 3},
            {"front": "Q2", "back": "A2", "hint": "easy", "difficulty": 1},
        ]
        filepath = tmp_path / "extra_fields.json"
        filepath.write_text(json.dumps(cards_data), encoding="utf-8")

        cards = load_flashcards(str(filepath))

        assert len(cards) == 2
        assert cards[0].front == "Q1"
        assert cards[1].back == "A2"


# ---------------------------------------------------------------------------
# Test 2 — SequentialMode with a single card
# ---------------------------------------------------------------------------


class TestSequentialWithSingleCard:
    """SequentialMode over a one-card deck returns the card then None."""

    def test_sequential_with_single_card(
        self, single_card_deck: list[FlashCard],
    ) -> None:
        """get_next_card() returns the sole card first, then None."""
        mode = SequentialMode(single_card_deck)

        assert mode.get_next_card() == single_card_deck[0]
        assert mode.get_next_card() is None


# ---------------------------------------------------------------------------
# Test 3 — AdaptiveMode: wrong then correct resolves the session
# ---------------------------------------------------------------------------


class TestAdaptiveWithAllWrongThenAllCorrect:
    """AdaptiveMode ends once all pending cards are answered correctly."""

    def test_adaptive_with_all_wrong_then_all_correct(
        self, single_card_deck: list[FlashCard],
    ) -> None:
        """Wrong re-queues; correct ends the session."""
        mode = AdaptiveMode(single_card_deck)
        card = single_card_deck[0]

        first = mode.get_next_card()
        assert first == card
        mode.record_answer(card, False)

        second = mode.get_next_card()
        assert second == card
        mode.record_answer(card, True)

        assert mode.get_next_card() is None


# ---------------------------------------------------------------------------
# Test 4 — SessionStats with zero questions avoids division by zero
# ---------------------------------------------------------------------------


class TestStatsWithZeroQuestions:
    """SessionStats.accuracy returns 0.0 with total=0."""

    def test_stats_with_zero_questions(self) -> None:
        """No ZeroDivisionError."""
        stats = SessionStats(total=0, correct=0, incorrect=0)
        assert stats.accuracy == 0.0


# ---------------------------------------------------------------------------
# Test 5 — QuizSession.answer handles Unicode input correctly
# ---------------------------------------------------------------------------


class TestAnswerWithUnicodeInput:
    """QuizSession.answer matches Unicode answers case-insensitively."""

    def test_answer_with_unicode_input_exact(self) -> None:
        """Exact Unicode answer is accepted."""
        card = FlashCard(front="Favourite drink?", back="café")
        session = QuizSession([card], SequentialMode([card]))
        assert session.answer(card, "café") is True

    def test_answer_with_unicode_input_case_insensitive(self) -> None:
        """Unicode answer differing only in case is still accepted."""
        card = FlashCard(front="Favourite drink?", back="café")
        session = QuizSession([card], SequentialMode([card]))
        assert session.answer(card, "CAFÉ") is True


# ---------------------------------------------------------------------------
# Test 6 — File path with spaces in the directory name
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestFilePathWithSpaces:
    """load_flashcards handles paths with spaces."""

    def test_file_path_with_spaces(self, tmp_path: pathlib.Path) -> None:
        """Loads from a directory whose name contains spaces."""
        spaced_dir = tmp_path / "my flash cards"
        spaced_dir.mkdir()
        filepath = spaced_dir / "deck.json"
        filepath.write_text(
            json.dumps([{"front": "Q", "back": "A"}]), encoding="utf-8",
        )

        cards = load_flashcards(str(filepath))

        assert len(cards) == 1
        assert cards[0].front == "Q"


# ---------------------------------------------------------------------------
# Test 7 — Concurrent sessions are independent
# ---------------------------------------------------------------------------


class TestConcurrentSessionsIndependent:
    """Two QuizSession instances are fully independent."""

    def test_concurrent_sessions_independent(
        self, sample_deck: list[FlashCard],
    ) -> None:
        """Wrong in session1 does not affect session2."""
        s1 = QuizSession(sample_deck, SequentialMode(sample_deck))
        s2 = QuizSession(sample_deck, SequentialMode(sample_deck))

        s1.answer(s1.next_card(), "wrong")  # type: ignore[arg-type]
        c2 = s2.next_card()
        s2.answer(c2, c2.back)  # type: ignore[arg-type]

        assert s1.get_stats().incorrect == 1
        assert s2.get_stats().correct == 1


# ---------------------------------------------------------------------------
# Coverage gap tests
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestCoverageGaps:
    """Targeted tests for previously uncovered branches."""

    def test_unsupported_json_format_raises(
        self, tmp_path: pathlib.Path,
    ) -> None:
        """data_loader.py:65 — JSON string (not list/dict) → SystemExit."""
        filepath = tmp_path / "string.json"
        filepath.write_text(json.dumps("just a string"), encoding="utf-8")
        with pytest.raises(SystemExit, match="Unsupported format"):
            load_flashcards(str(filepath))

    def test_commonpath_value_error_rejects(self) -> None:
        """file_handler.py:35-37 — commonpath ValueError (e.g. Windows drives)
        must reject the path, not crash."""
        with patch(
            "utils.file_handler.os.path.commonpath",
            side_effect=ValueError("no common path"),
        ):
            with pytest.raises(ValueError, match="outside the allowed"):
                _validate_path("data/python_basics.json")

    def test_file_disappears_after_size_check(
        self, tmp_path: pathlib.Path,
    ) -> None:
        """file_handler.py:77-78 — file deleted between getsize and open."""
        filepath = tmp_path / "vanish.json"
        filepath.write_text(
            json.dumps([{"front": "Q", "back": "A"}]), encoding="utf-8",
        )

        def disappearing_open(path: object, **kwargs: object) -> object:
            raise FileNotFoundError("gone")

        with patch("builtins.open", side_effect=disappearing_open):
            with pytest.raises(SystemExit, match="not found"):
                load_flashcards(str(filepath))

    def test_run_generic_exception_in_load(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """main.py:59-61 — non-SystemExit exception from load_flashcards."""
        monkeypatch.setattr(
            "main.load_flashcards",
            lambda _: (_ for _ in ()).throw(RuntimeError("db error")),
        )
        with pytest.raises(SystemExit):
            run(["-f", "data/python_basics.json"])
