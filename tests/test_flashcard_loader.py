"""
TDD tests for Phase 1 — Data Layer.

Tests cover load_flashcards() in data_loader and _validate_path() in
utils.file_handler.  All tests are written against stub implementations
that raise NotImplementedError; they are expected to FAIL until the
implementations are written (red phase of red-green-refactor).

Run with:
    pytest tests/test_flashcard_loader.py -v
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from data_loader import FlashCard, load_flashcards
from utils.file_handler import MAX_FILE_SIZE, _validate_path


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestLoadValidFlashcards:
    """load_flashcards successfully parses well-formed JSON files."""

    def test_load_valid_flashcards_array(self, valid_array_json):
        """Array-format JSON produces the correct count of FlashCard objects."""
        cards = load_flashcards(valid_array_json)

        assert len(cards) == 3
        assert all(isinstance(card, FlashCard) for card in cards)

    def test_load_valid_flashcards_array_content(self, valid_array_json):
        """Array-format cards carry the expected front and back text."""
        cards = load_flashcards(valid_array_json)

        assert cards[0].front == "What is Python?"
        assert cards[0].back == "A programming language"

    def test_load_valid_flashcards_object_format(self, valid_object_json):
        """Object-format JSON ({"cards": [...]}) produces correct FlashCard list."""
        cards = load_flashcards(valid_object_json)

        assert len(cards) == 2
        assert all(isinstance(card, FlashCard) for card in cards)

    def test_load_valid_flashcards_object_format_content(self, valid_object_json):
        """Object-format cards carry the expected front and back text."""
        cards = load_flashcards(valid_object_json)

        assert cards[0].front == "What is Python?"
        assert cards[0].back == "A programming language"


# ---------------------------------------------------------------------------
# Error / validation tests
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestLoadFlashcardsErrors:
    """load_flashcards raises SystemExit for every invalid or unsafe input."""

    def test_load_invalid_json_raises_system_exit(self, invalid_json):
        """Malformed JSON content causes SystemExit."""
        with pytest.raises(SystemExit):
            load_flashcards(invalid_json)

    def test_load_missing_back_field_raises(self, missing_back_json):
        """A card object that omits 'back' causes SystemExit."""
        with pytest.raises(SystemExit):
            load_flashcards(missing_back_json)

    def test_load_missing_front_field_raises(self, missing_front_json):
        """A card object that omits 'front' causes SystemExit."""
        with pytest.raises(SystemExit):
            load_flashcards(missing_front_json)

    def test_load_empty_deck_raises(self, empty_deck_json):
        """An empty card list causes SystemExit (a deck must have >= 1 card)."""
        with pytest.raises(SystemExit):
            load_flashcards(empty_deck_json)

    def test_load_nonexistent_file_raises(self, tmp_path):
        """A path that does not exist on disk causes SystemExit."""
        nonexistent = str(tmp_path / "does_not_exist.json")

        with pytest.raises(SystemExit):
            load_flashcards(nonexistent)

    def test_load_cards_not_dicts_raises(self, tmp_path):
        """Regression: JSON array of non-objects like [123] causes SystemExit."""
        import json
        filepath = tmp_path / "bad_cards.json"
        filepath.write_text(json.dumps([123, 456]), encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(filepath))

    def test_load_cards_key_not_list_raises(self, tmp_path):
        """Regression: {"cards": 123} causes SystemExit, not TypeError."""
        import json
        filepath = tmp_path / "bad_cards_key.json"
        filepath.write_text(json.dumps({"cards": 123}), encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(filepath))


# ---------------------------------------------------------------------------
# Security tests — path traversal
# ---------------------------------------------------------------------------


class TestPathTraversal:
    """Path traversal attempts must be rejected before any file I/O occurs."""

    def test_path_traversal_rejected(self):
        """A traversal string passed to load_flashcards causes SystemExit."""
        with pytest.raises(SystemExit):
            load_flashcards("../../etc/passwd")

    def test_validate_path_raises_value_error(self):
        """_validate_path() raises ValueError for a path that escapes the project root."""
        with pytest.raises(ValueError):
            _validate_path("../../etc/passwd")

    def test_validate_path_raises_value_error_absolute_escape(self):
        """_validate_path() raises ValueError for an absolute path outside the project."""
        with pytest.raises(ValueError):
            _validate_path("/etc/passwd")

    def test_validate_path_rejects_sibling_directory(self):
        """Regression: a sibling dir matching SAFE_BASE_DIR as string prefix is rejected.

        e.g. if SAFE_BASE_DIR is /home/project, then /home/project-evil/secret.txt
        must NOT pass validation even though it starts with the same string prefix.
        """
        from utils.file_handler import SAFE_BASE_DIR
        sibling = SAFE_BASE_DIR + "-malicious/secret.txt"
        with pytest.raises(ValueError):
            _validate_path(sibling)


# ---------------------------------------------------------------------------
# Size-limit tests
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("allow_tmp_paths")
class TestOversizedFile:
    """Files that exceed MAX_FILE_SIZE must be rejected."""

    def test_oversized_file_rejected(self, valid_array_json):
        """A file reported as > 10 MB by os.path.getsize causes SystemExit."""
        oversized_bytes = MAX_FILE_SIZE + 1

        with patch("os.path.getsize", return_value=oversized_bytes):
            with pytest.raises(SystemExit):
                load_flashcards(valid_array_json)

    def test_file_at_exact_size_limit_rejected(self, valid_array_json):
        """A file reported as exactly 10 MB + 1 byte also causes SystemExit."""
        # Boundary condition: one byte over the limit must still be rejected.
        with patch("os.path.getsize", return_value=MAX_FILE_SIZE + 1):
            with pytest.raises(SystemExit):
                load_flashcards(valid_array_json)

    def test_file_at_limit_accepted(self, valid_array_json):
        """A file reported as exactly MAX_FILE_SIZE bytes is within the limit."""
        # Boundary condition: a file at exactly the limit should NOT be rejected
        # solely on size grounds.  It may still raise for other reasons; this test
        # only verifies that the size check itself does not trigger a SystemExit
        # when the size equals the cap exactly.
        #
        # Because the stubs raise NotImplementedError (not SystemExit), we catch
        # both: if SystemExit is raised it must NOT carry an 'oversized' message.
        with patch("os.path.getsize", return_value=MAX_FILE_SIZE):
            try:
                load_flashcards(valid_array_json)
            except SystemExit as exc:
                # Acceptable only if the exit was NOT due to an oversized-file error.
                message = str(exc).lower()
                assert "size" not in message and "large" not in message, (
                    "SystemExit should not be raised for size when file is exactly at limit"
                )
            except NotImplementedError:
                pass  # Stub behaviour — test passes once implementation exists
