"""
Quiz engine with Strategy Pattern for quiz modes and Factory for mode creation.

Provides SequentialMode, RandomMode, AdaptiveMode, and a QuizSession orchestrator.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field

from data_loader import FlashCard


class QuizMode(ABC):
    """Abstract base class for quiz selection strategies."""

    @abstractmethod
    def get_next_card(self) -> FlashCard | None:
        """Return the next card or None if the session is over."""


class SequentialMode(QuizMode):
    """Present cards in order from first to last."""

    def __init__(self, deck: list[FlashCard]) -> None:
        self._cards = list(deck)
        self._index = 0

    def get_next_card(self) -> FlashCard | None:
        """Return next card in order, or None when exhausted."""
        if self._index >= len(self._cards):
            return None
        card = self._cards[self._index]
        self._index += 1
        return card


class RandomMode(QuizMode):
    """Present all cards in shuffled order, no repeats."""

    def __init__(self, deck: list[FlashCard]) -> None:
        self._cards = list(deck)
        random.shuffle(self._cards)
        self._index = 0

    def get_next_card(self) -> FlashCard | None:
        """Return next card in shuffled order, or None when exhausted."""
        if self._index >= len(self._cards):
            return None
        card = self._cards[self._index]
        self._index += 1
        return card


class AdaptiveMode(QuizMode):
    """Repeat missed cards until all are answered correctly.

    Cards are served from a queue. Incorrect answers re-enqueue the card.
    The session ends when the queue is empty (all answered correctly)
    or the retry cap is reached (len(deck) * 3 total serves).
    """

    def __init__(self, deck: list[FlashCard]) -> None:
        self._queue: deque[FlashCard] = deque(deck)
        self._max_serves = len(deck) * 3
        self._serve_count = 0
        self._exhausted = False

    @property
    def was_force_stopped(self) -> bool:
        """True if the session ended due to retry cap, not all-correct."""
        return self._exhausted

    def get_next_card(self) -> FlashCard | None:
        """Return next card from queue, or None when done or cap reached."""
        if not self._queue:
            return None
        if self._serve_count >= self._max_serves:
            self._exhausted = True
            return None
        self._serve_count += 1
        return self._queue.popleft()

    def record_answer(self, card: FlashCard, correct: bool) -> None:
        """Re-enqueue the card if the answer was wrong."""
        if not correct:
            self._queue.append(card)


class QuizModeFactory:
    """Factory for creating QuizMode instances by name."""

    _MODES: dict[str, type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @staticmethod
    def create(mode: str, deck: list[FlashCard]) -> QuizMode:
        """Create a QuizMode by name (case-insensitive).

        Raises:
            ValueError: If the mode name is not recognized.
        """
        key = mode.strip().lower()
        mode_cls = QuizModeFactory._MODES.get(key)
        if mode_cls is None:
            valid = ", ".join(sorted(QuizModeFactory._MODES))
            raise ValueError(
                f"Unknown quiz mode '{mode}'. Valid modes: {valid}"
            )
        return mode_cls(deck)  # type: ignore[call-arg]


@dataclass
class SessionStats:
    """Statistics for a completed quiz session."""

    total: int
    correct: int
    incorrect: int
    missed_cards: list[FlashCard] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Computed from correct/total to avoid inconsistency."""
        return (self.correct / self.total * 100) if self.total > 0 else 0.0


class QuizSession:
    """Orchestrates a complete quiz session."""

    def __init__(self, deck: list[FlashCard], mode: QuizMode) -> None:
        if not deck:
            raise ValueError("Deck must contain at least one card.")
        self._deck = deck
        self._mode = mode
        self._total = 0
        self._correct = 0
        self._incorrect = 0
        self._missed: list[FlashCard] = []
        self._missed_ids: set[int] = set()

    def next_card(self) -> FlashCard | None:
        """Return the next card from the mode, or None if done."""
        return self._mode.get_next_card()

    def answer(self, card: FlashCard, user_input: str) -> bool:
        """Check user_input against card.back (case-insensitive, stripped).

        Returns True if correct.
        """
        self._total += 1
        is_correct = user_input.strip().lower() == card.back.strip().lower()
        if is_correct:
            self._correct += 1
        else:
            self._incorrect += 1
            # Track by identity (id) so duplicate-valued cards are counted
            if id(card) not in self._missed_ids:
                self._missed_ids.add(id(card))
                self._missed.append(card)
        # Notify adaptive mode about the answer
        if isinstance(self._mode, AdaptiveMode):
            self._mode.record_answer(card, is_correct)
        return is_correct

    def get_stats(self) -> SessionStats:
        """Return current session statistics."""
        return SessionStats(
            total=self._total,
            correct=self._correct,
            incorrect=self._incorrect,
            missed_cards=list(self._missed),
        )
