"""
Main entry point for the Flashcard Quizzer CLI.

Orchestrates data loading, quiz engine, and terminal UI into a complete session.
"""
from __future__ import annotations

import argparse
import sys

import colorama

import ui
from data_loader import load_flashcards
from quiz_engine import AdaptiveMode, QuizModeFactory, QuizSession

colorama.init(autoreset=True)

__version__ = "1.0.0"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer — test your knowledge from the terminal.",
    )
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Path to a JSON flashcard file.",
    )
    parser.add_argument(
        "-m", "--mode",
        default="sequential",
        help="Quiz mode: sequential, random, or adaptive (default: sequential).",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=True,
        help="Show session stats at the end (default: always shown).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> None:
    """Main entry point — orchestrates the full quiz session."""
    args = parse_args(argv)

    try:
        deck = load_flashcards(args.file)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    try:
        mode = QuizModeFactory.create(args.mode, deck)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    session = QuizSession(deck, mode)
    ui.display_welcome(len(deck), args.mode)

    try:
        card = session.next_card()
        while card is not None:
            ui.display_card(card)
            user_input = ui.get_user_answer()
            correct = session.answer(card, user_input)
            ui.display_feedback(correct, card.back)
            card = session.next_card()
    except SystemExit:
        # User typed 'exit' or Ctrl+C — show stats before leaving
        pass
    except Exception as exc:
        # Catch all unexpected errors so user never sees a raw traceback
        print("\nError: An unexpected error occurred.", file=sys.stderr)
        print(f"Details: {exc}", file=sys.stderr)

    # Warn if adaptive mode hit the retry cap
    if isinstance(mode, AdaptiveMode) and mode.was_force_stopped:
        print(
            "\nNote: Adaptive mode stopped early (retry limit reached)."
            " Some cards were not answered correctly."
        )

    ui.display_stats(session.get_stats())


if __name__ == "__main__":
    run()
