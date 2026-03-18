"""
Edge case and hardening tests for the Flashcard Quizzer.

These tests exercise boundary conditions and stress scenarios that complement
the core TDD suite: extra JSON fields, single-card decks, adaptive exhaustion,
zero-question stats, Unicode answers, paths with spaces, and concurrent sessions.

Run with:
    python3 -m pytest tests/test_edge_cases.py -v --no-header --tb=short
"""
from __future__ import annotations

import json

import pytest

from data_loader import FlashCard, load_flashcards
from quiz_engine import (
    AdaptiveMode,
    QuizSession,
    SequentialMode,
    SessionStats,
)


# ---------------------------------------------------------------------------
# Test 1 — Extra JSON fields are silently accepted
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestLoadJsonWithExtraFields:
    """load_flashcards must ignore unknown keys beyond 'front' and 'back'."""

    def test_load_json_with_extra_fields_is_accepted(self, tmp_path):
        """Cards with bonus keys like 'hint' and 'difficulty' load without error."""
        cards_data = [
            {"front": "Q1", "back": "A1", "hint": "think carefully", "difficulty": 3},
            {"front": "Q2", "back": "A2", "hint": "easy one", "difficulty": 1},
        ]
        filepath = tmp_path / "extra_fields.json"
        filepath.write_text(json.dumps(cards_data), encoding="utf-8")

        cards = load_flashcards(str(filepath))

        assert len(cards) == 2
        assert all(isinstance(card, FlashCard) for card in cards)
        assert cards[0].front == "Q1"
        assert cards[0].back == "A1"
        assert cards[1].front == "Q2"
        assert cards[1].back == "A2"


# ---------------------------------------------------------------------------
# Test 2 — SequentialMode with a single card
# ---------------------------------------------------------------------------


class TestSequentialWithSingleCard:
    """SequentialMode over a one-card deck returns the card then None."""

    def test_sequential_with_single_card(self, single_card_deck):
        """get_next_card() returns the sole card first, then None on the next call."""
        mode = SequentialMode(single_card_deck)

        card = mode.get_next_card()
        sentinel = mode.get_next_card()

        assert card == single_card_deck[0]
        assert sentinel is None


# ---------------------------------------------------------------------------
# Test 3 — AdaptiveMode: wrong then correct resolves the session
# ---------------------------------------------------------------------------


class TestAdaptiveWithAllWrongThenAllCorrect:
    """AdaptiveMode ends only once all pending cards are answered correctly."""

    def test_adaptive_with_all_wrong_then_all_correct(self, single_card_deck):
        """Wrong answer re-queues the card; subsequent correct answer ends the session."""
        mode = AdaptiveMode(single_card_deck)
        card = single_card_deck[0]

        # First serve — answer wrong, card is re-enqueued.
        first_serve = mode.get_next_card()
        assert first_serve == card
        mode.record_answer(card, False)

        # Second serve — the same card must come back.
        second_serve = mode.get_next_card()
        assert second_serve == card
        mode.record_answer(card, True)

        # Queue is now empty — session must end.
        assert mode.get_next_card() is None


# ---------------------------------------------------------------------------
# Test 4 — SessionStats with zero questions avoids division by zero
# ---------------------------------------------------------------------------


class TestStatsWithZeroQuestions:
    """SessionStats.accuracy returns 0.0 when no questions have been answered."""

    def test_stats_with_zero_questions(self):
        """accuracy is 0.0 for a stats object with total=0 — no ZeroDivisionError."""
        stats = SessionStats(total=0, correct=0, incorrect=0)

        assert stats.accuracy == 0.0


# ---------------------------------------------------------------------------
# Test 5 — QuizSession.answer handles Unicode input correctly
# ---------------------------------------------------------------------------


class TestAnswerWithUnicodeInput:
    """QuizSession.answer matches Unicode answers case-insensitively."""

    def test_answer_with_unicode_input_exact(self):
        """Exact Unicode answer is accepted."""
        card = FlashCard(front="Favourite drink?", back="café")
        mode = SequentialMode([card])
        session = QuizSession([card], mode)

        result = session.answer(card, "café")

        assert result is True

    def test_answer_with_unicode_input_case_insensitive(self):
        """Unicode answer differing only in case is still accepted."""
        card = FlashCard(front="Favourite drink?", back="café")
        mode = SequentialMode([card])
        session = QuizSession([card], mode)

        result = session.answer(card, "CAFÉ")

        assert result is True


# ---------------------------------------------------------------------------
# Test 6 — File path with spaces in the directory name
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestFilePathWithSpaces:
    """load_flashcards handles paths whose directory component contains spaces."""

    def test_file_path_with_spaces(self, tmp_path):
        """A JSON file inside a directory named with spaces loads correctly."""
        spaced_dir = tmp_path / "my flash cards"
        spaced_dir.mkdir()

        cards_data = [
            {"front": "What is 2+2?", "back": "4"},
        ]
        filepath = spaced_dir / "deck.json"
        filepath.write_text(json.dumps(cards_data), encoding="utf-8")

        cards = load_flashcards(str(filepath))

        assert len(cards) == 1
        assert isinstance(cards[0], FlashCard)
        assert cards[0].front == "What is 2+2?"
        assert cards[0].back == "4"


# ---------------------------------------------------------------------------
# Test 7 — Two concurrent QuizSessions share the deck but have independent stats
# ---------------------------------------------------------------------------


class TestConcurrentSessionsIndependent:
    """Two QuizSession instances created from the same deck are fully independent."""

    def test_concurrent_sessions_independent(self, sample_deck):
        """Wrong answer in session1 does not affect session2's stats, and vice versa."""
        mode1 = SequentialMode(sample_deck)
        mode2 = SequentialMode(sample_deck)
        session1 = QuizSession(sample_deck, mode1)
        session2 = QuizSession(sample_deck, mode2)

        card1 = session1.next_card()
        session1.answer(card1, "wrong answer")

        card2 = session2.next_card()
        session2.answer(card2, card2.back)  # correct

        stats1 = session1.get_stats()
        stats2 = session2.get_stats()

        assert stats1.correct == 0
        assert stats1.incorrect == 1

        assert stats2.correct == 1
        assert stats2.incorrect == 0
