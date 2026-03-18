"""
TDD integration tests for Phase 4 — CLI entry point (main.py).

Tests cover parse_args() and run() in main.py.  All tests are written
against the *final* API described in the Phase 4 specification; they are
expected to FAIL until main.py is fully implemented (red phase of
red-green-refactor).

Run with:
    pytest tests/test_integration.py -v
"""
from __future__ import annotations

import pytest

import ui
from main import parse_args, run


# ---------------------------------------------------------------------------
# Correct answers for data/python_basics.json (10 cards, sequential order).
# Each string matches card["back"] exactly (case-insensitive comparison is
# used by QuizSession.answer, so canonical casing is fine here).
# ---------------------------------------------------------------------------

_PYTHON_BASICS_ANSWERS: list[str] = [
    "A named reference that stores a value in memory, created by assignment"
    " with the = operator.",
    "Use square brackets with comma-separated values, e.g. my_list = [1, 2, 3].",
    'An unordered collection of key-value pairs defined with curly braces,'
    ' e.g. {"name": "Alice"}.',
    "Tuples are immutable sequences created with parentheses, so their elements"
    " cannot be changed after creation.",
    "Use the def keyword followed by the function name, parentheses for"
    " parameters, and a colon.",
    "for loops iterate over sequences, while while loops repeat as long as a"
    " condition is true.",
    "Use the class keyword followed by the class name, with __init__ as the"
    " constructor method.",
    "A formatted string literal prefixed with f that allows embedding"
    " expressions inside curly braces.",
    "True and False, which are capitalized keywords used for logical operations.",
    "Use the import statement, e.g. import math, or from math import sqrt for"
    " specific items.",
]


# ---------------------------------------------------------------------------
# parse_args tests
# ---------------------------------------------------------------------------


class TestParseArgs:
    """Unit-level tests for the argument parser."""

    def test_main_requires_file_argument(self):
        """parse_args([]) must raise SystemExit because -f/--file is required."""
        with pytest.raises(SystemExit):
            parse_args([])

    def test_main_default_mode_is_sequential(self):
        """parse_args with only -f must default --mode to 'sequential'."""
        args = parse_args(["-f", "data/test.json"])

        assert args.mode == "sequential"


# ---------------------------------------------------------------------------
# run() error-handling tests
# ---------------------------------------------------------------------------


class TestRunErrorHandling:
    """Verify that run() exits cleanly on bad input without printing tracebacks."""

    def test_main_invalid_mode_exits_cleanly(self, capsys):
        """run() with an unrecognised mode must raise SystemExit with no traceback."""
        with pytest.raises(SystemExit):
            run(["-f", "data/python_basics.json", "-m", "badmode"])

        captured = capsys.readouterr()
        assert "Traceback" not in captured.out
        assert "Traceback" not in captured.err

    def test_main_nonexistent_file_exits_cleanly(self, capsys):
        """run() with a missing file must raise SystemExit with no traceback."""
        with pytest.raises(SystemExit):
            run(["-f", "nonexistent.json"])

        captured = capsys.readouterr()
        assert "Traceback" not in captured.out
        assert "Traceback" not in captured.err


# ---------------------------------------------------------------------------
# Smoke tests — full quiz loop via mocked UI
# ---------------------------------------------------------------------------


class TestRunSmoke:
    """End-to-end smoke tests that drive a full quiz session with mocked input."""

    def test_main_smoke_sequential(self, monkeypatch):
        """run() completes a sequential session when given correct answers.

        get_user_answer is replaced with a side_effect that returns each
        correct answer in order.  After all 10 cards are served the loop
        exits normally (or via SystemExit(0) from display_stats / EOF
        handling), so we allow both outcomes.
        """
        answers = iter(_PYTHON_BASICS_ANSWERS)
        monkeypatch.setattr(ui, "get_user_answer", lambda: next(answers))

        try:
            run(["-f", "data/python_basics.json", "-m", "sequential"])
        except SystemExit as exc:
            # SystemExit(0) is the only acceptable exit code for a clean finish.
            assert exc.code == 0 or exc.code is None

    def test_main_smoke_adaptive(self, monkeypatch):
        """run() completes an adaptive session when every answer is correct.

        With all-correct answers AdaptiveMode never re-enqueues a card, so
        the session finishes after exactly 10 serves — same answer list works.
        """
        answers = iter(_PYTHON_BASICS_ANSWERS)
        monkeypatch.setattr(ui, "get_user_answer", lambda: next(answers))

        try:
            run(["-f", "data/python_basics.json", "-m", "adaptive"])
        except SystemExit as exc:
            assert exc.code == 0 or exc.code is None

    def test_unexpected_error_no_traceback(self, monkeypatch, capsys):
        """Regression: unexpected RuntimeError in UI does not leak a traceback."""
        call_count = 0

        def exploding_answer() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("boom")
            return "exit"

        monkeypatch.setattr(ui, "get_user_answer", exploding_answer)

        try:
            run(["-f", "data/python_basics.json", "-m", "sequential"])
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "Traceback" not in captured.out
        assert "Traceback" not in captured.err

    def test_adaptive_force_stop_warning(self, monkeypatch, capsys):
        """Regression: adaptive retry-cap exhaustion prints a warning."""
        # Always answer wrong so adaptive mode hits the cap
        monkeypatch.setattr(ui, "get_user_answer", lambda: "wrong")

        try:
            run(["-f", "data/python_basics.json", "-m", "adaptive"])
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "stopped early" in captured.out.lower() or \
            "retry limit" in captured.out.lower()
