"""
TDD tests for Phase 2 — Quiz Engine.

Tests cover QuizModeFactory, SequentialMode, RandomMode, AdaptiveMode,
SessionStats, and QuizSession.  All tests are written against stub
implementations that raise NotImplementedError; they are expected to FAIL
until the implementations are written (red phase of red-green-refactor).

Run with:
    pytest tests/test_quiz_modes.py -v
"""
from __future__ import annotations

import pytest

from data_loader import FlashCard
from quiz_engine import (
    AdaptiveMode,
    QuizModeFactory,
    QuizSession,
    RandomMode,
    SequentialMode,
    SessionStats,
)


# ---------------------------------------------------------------------------
# QuizModeFactory tests
# ---------------------------------------------------------------------------


class TestQuizModeFactory:
    """QuizModeFactory.create() resolves mode names to the correct classes."""

    def test_factory_returns_sequential_mode(self, sample_deck):
        """'sequential' produces a SequentialMode instance."""
        mode = QuizModeFactory.create("sequential", sample_deck)

        assert isinstance(mode, SequentialMode)

    def test_factory_returns_random_mode(self, sample_deck):
        """'random' produces a RandomMode instance."""
        mode = QuizModeFactory.create("random", sample_deck)

        assert isinstance(mode, RandomMode)

    def test_factory_returns_adaptive_mode(self, sample_deck):
        """'adaptive' produces an AdaptiveMode instance."""
        mode = QuizModeFactory.create("adaptive", sample_deck)

        assert isinstance(mode, AdaptiveMode)

    def test_factory_case_insensitive(self, sample_deck):
        """Mode names are matched regardless of capitalisation."""
        upper_mode = QuizModeFactory.create("SEQUENTIAL", sample_deck)
        title_mode = QuizModeFactory.create("Sequential", sample_deck)

        assert isinstance(upper_mode, SequentialMode)
        assert isinstance(title_mode, SequentialMode)

    def test_factory_raises_for_unknown_mode(self, sample_deck):
        """An unrecognised mode name raises ValueError."""
        with pytest.raises(ValueError):
            QuizModeFactory.create("badmode", sample_deck)


# ---------------------------------------------------------------------------
# SequentialMode tests
# ---------------------------------------------------------------------------


class TestSequentialMode:
    """SequentialMode returns cards in deck order then None."""

    def test_sequential_exhausts_deck_in_order(self, sample_deck):
        """Cards are returned in original deck order; None signals exhaustion."""
        mode = SequentialMode(sample_deck)

        first = mode.get_next_card()
        second = mode.get_next_card()
        third = mode.get_next_card()
        sentinel = mode.get_next_card()

        assert first == sample_deck[0]
        assert second == sample_deck[1]
        assert third == sample_deck[2]
        assert sentinel is None


# ---------------------------------------------------------------------------
# RandomMode tests
# ---------------------------------------------------------------------------


class TestRandomMode:
    """RandomMode returns every card exactly once in an unspecified order."""

    def test_random_mode_returns_all_cards_no_repeats(self, sample_deck):
        """All card fronts appear exactly once; no card is skipped or duplicated."""
        mode = RandomMode(sample_deck)

        returned_fronts = set()
        card = mode.get_next_card()
        while card is not None:
            returned_fronts.add(card.front)
            card = mode.get_next_card()

        expected_fronts = {c.front for c in sample_deck}
        assert returned_fronts == expected_fronts


# ---------------------------------------------------------------------------
# AdaptiveMode tests
# ---------------------------------------------------------------------------


class TestAdaptiveMode:
    """AdaptiveMode re-queues incorrectly answered cards until all are correct."""

    def test_adaptive_mode_repeats_missed_cards(self, sample_deck):
        """A card answered incorrectly via record_answer reappears later."""
        mode = AdaptiveMode(sample_deck)

        first_card = mode.get_next_card()
        assert first_card is not None

        # Mark the first card as wrong — it must reappear at some future point.
        mode.record_answer(first_card, correct=False)

        remaining_cards: list[FlashCard] = []
        card = mode.get_next_card()
        while card is not None:
            remaining_cards.append(card)
            # Answer all subsequent cards correctly so the session can end.
            mode.record_answer(card, correct=True)
            card = mode.get_next_card()

        remaining_fronts = [c.front for c in remaining_cards]
        assert first_card.front in remaining_fronts

    def test_adaptive_mode_ends_only_when_all_correct(self, sample_deck):
        """get_next_card() returns None only after every card is answered correctly."""
        mode = AdaptiveMode(sample_deck)

        card = mode.get_next_card()
        while card is not None:
            mode.record_answer(card, correct=True)
            card = mode.get_next_card()

        # After all cards answered correctly, the mode must signal completion.
        assert mode.get_next_card() is None


# ---------------------------------------------------------------------------
# SessionStats tests
# ---------------------------------------------------------------------------


class TestSessionStats:
    """SessionStats.accuracy is computed correctly from correct and total counts."""

    def test_session_stats_accuracy_calculation(self):
        """accuracy returns the correct percentage given total=10, correct=8."""
        stats = SessionStats(total=10, correct=8, incorrect=2)

        assert stats.accuracy == 80.0


# ---------------------------------------------------------------------------
# QuizSession tests
# ---------------------------------------------------------------------------


class TestQuizSession:
    """QuizSession orchestrates card delivery, answer checking, and statistics."""

    def test_answer_is_case_insensitive(self, sample_deck):
        """answer() accepts input whose case differs from card.back."""
        mode = SequentialMode(sample_deck)
        session = QuizSession(sample_deck, mode)

        # sample_deck[0].back == "A programming language"
        card = session.next_card()
        assert card is not None
        result = session.answer(card, "A PROGRAMMING LANGUAGE")

        assert result is True

    def test_answer_strips_leading_trailing_whitespace(self, sample_deck):
        """answer() treats input with surrounding spaces as equal to card.back."""
        mode = SequentialMode(sample_deck)
        session = QuizSession(sample_deck, mode)

        # sample_deck[0].back == "A programming language"
        card = session.next_card()
        assert card is not None
        result = session.answer(card, "  A programming language  ")

        assert result is True

    def test_session_tracks_missed_cards_correctly(self, sample_deck):
        """get_stats().missed_cards contains exactly the cards answered incorrectly."""
        mode = SequentialMode(sample_deck)
        session = QuizSession(sample_deck, mode)

        first_card = session.next_card()
        assert first_card is not None
        session.answer(first_card, "wrong answer")  # deliberately incorrect

        second_card = session.next_card()
        assert second_card is not None
        session.answer(second_card, second_card.back)  # correct

        stats = session.get_stats()

        assert first_card in stats.missed_cards
        assert second_card not in stats.missed_cards

    def test_session_rejects_empty_deck(self):
        """Regression: QuizSession with empty deck raises ValueError."""
        mode = SequentialMode([])
        with pytest.raises(ValueError, match="at least one card"):
            QuizSession([], mode)

    def test_missed_cards_tracks_duplicates_by_identity(self):
        """Regression: two cards with same front/back are tracked separately."""
        card_a = FlashCard(front="Q", back="A")
        card_b = FlashCard(front="Q", back="A")
        deck = [card_a, card_b]
        mode = SequentialMode(deck)
        session = QuizSession(deck, mode)

        c1 = session.next_card()
        assert c1 is not None
        session.answer(c1, "wrong")
        c2 = session.next_card()
        assert c2 is not None
        session.answer(c2, "wrong")

        stats = session.get_stats()
        assert len(stats.missed_cards) == 2

    def test_adaptive_force_stop_is_detectable(self):
        """Regression: retry cap sets was_force_stopped, not silent completion."""
        deck = [FlashCard(front="Q", back="A")]
        mode = AdaptiveMode(deck)

        card = mode.get_next_card()
        while card is not None:
            mode.record_answer(card, correct=False)
            card = mode.get_next_card()

        assert mode.was_force_stopped is True
