"""
Terminal UI for the Flashcard Quizzer CLI.

Provides colored output, user input handling, and stats display.
Note: colorama.init() is called in main.py, NOT here.
"""
from __future__ import annotations

from colorama import Fore, Style

from data_loader import FlashCard
from quiz_engine import SessionStats

MAX_INPUT_LENGTH = 500


def display_welcome(deck_size: int, mode: str) -> None:
    """Display welcome message with deck size and mode."""
    print(f"\n{Fore.CYAN}{'=' * 40}")
    print(" Flashcard Quizzer")
    print(f"{'=' * 40}{Style.RESET_ALL}")
    print(f" Deck size : {deck_size} cards")
    print(f" Mode      : {mode}")
    print(f" Type {Fore.YELLOW}'exit'{Style.RESET_ALL} to quit at any time.\n")


def display_card(card: FlashCard) -> None:
    """Display the front of a flashcard."""
    print(f"\n{Fore.CYAN}Question:{Style.RESET_ALL} {card.front}")


def get_user_answer() -> str:
    """Prompt for and return the user's answer (stripped, max 500 chars).

    Raises:
        SystemExit: If the user types 'exit', presses Ctrl+C, or EOF is reached.
    """
    try:
        raw = input("Your answer: ")
    except (KeyboardInterrupt, EOFError):
        print()  # newline after ^C / EOF
        raise SystemExit(0)

    stripped = raw.strip()
    if stripped.lower() == "exit":
        raise SystemExit(0)

    return stripped[:MAX_INPUT_LENGTH]


def display_feedback(correct: bool, expected: str) -> None:
    """Display colored feedback: green for correct, red for incorrect."""
    if correct:
        print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
    else:
        print(
            f"{Fore.RED}Incorrect!{Style.RESET_ALL}"
            f" Expected: {expected}"
        )


def display_stats(stats: SessionStats) -> None:
    """Display the session summary table with stats and missed cards."""
    border = "\u2550" * 28
    print(f"\n{border}")
    print(" SESSION SUMMARY")
    print(border)
    print(f" Total Questions : {stats.total}")
    print(f" Correct         : {stats.correct}")
    print(f" Incorrect       : {stats.incorrect}")
    print(f" Accuracy        : {stats.accuracy:.1f}%")
    print(border)

    if stats.missed_cards:
        print(f" {Fore.RED}Missed Cards:{Style.RESET_ALL}")
        for card in stats.missed_cards:
            print(f"  \u2022 {card.front} \u2192 {card.back}")
        print(border)
