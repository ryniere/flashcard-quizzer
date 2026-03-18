"""
Flashcard data loader with JSON validation.

Supports array format and object {"cards": [...]} format.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

from utils.file_handler import read_file


@dataclass
class FlashCard:
    """Represents a single flashcard with a front (question) and back (answer)."""

    front: str
    back: str


def load_flashcards(filepath: str) -> list[FlashCard]:
    """Load and validate flashcards from a JSON file.

    Supports two JSON formats:
    - Array format: ``[{"front": "...", "back": "..."}, ...]``
    - Object format: ``{"cards": [{"front": "...", "back": "..."}, ...]}``

    Args:
        filepath: Path to the JSON file containing flashcard data.

    Returns:
        A list of validated FlashCard objects.

    Raises:
        SystemExit: On any validation or I/O error, with a user-friendly message.
    """
    filename = os.path.basename(filepath)

    # Step 1: Read the file securely via file_handler
    try:
        content = read_file(filepath)
    except ValueError:
        raise SystemExit(
            f"Error: Access denied for '{filename}'\n"
            f"   Hint: The file path must stay within the project directory."
        )

    # Step 2: Parse JSON content
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise SystemExit(
            f"Error: Invalid JSON in '{filename}'\n"
            f"   Hint: Check the file for syntax errors."
        )

    # Step 3: Handle both array and object formats
    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict) and "cards" in data:
        cards = data["cards"]
    else:
        raise SystemExit(
            f"Error: Unsupported format in '{filename}'\n"
            f"   Hint: Use a JSON array or an object with a 'cards' key."
        )

    # Step 4: Validate the cards list
    if not cards:
        raise SystemExit(
            f"Error: No flashcards found in '{filename}'\n"
            f"   Hint: Add at least one card with 'front' and 'back' fields."
        )

    for card in cards:
        for field in ("front", "back"):
            if field not in card:
                raise SystemExit(
                    f"Error: Card is missing required field '{field}'"
                    f" in '{filename}'\n"
                    f"   Hint: Every card needs both 'front' and 'back' fields."
                )

    # Step 5: Build and return FlashCard objects
    return [FlashCard(front=card["front"], back=card["back"]) for card in cards]
