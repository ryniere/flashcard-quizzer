# Phase 1 — Data Layer & Validation

## Objective
Create a system to load and validate flashcard data from JSON files, with security
hardening (path traversal prevention, file size limits, input validation).

## Files to create/modify

| File | Action | Description |
|------|--------|-------------|
| `utils/file_handler.py` | **Rewrite** | Replace starter's `FileHandler` class with `read_file()` + `_validate_path()` functions for secure file I/O |
| `data_loader.py` | **Create** | `FlashCard` dataclass + `load_flashcards()` supporting array and object JSON formats |
| `data/python_basics.json` | **Create** | 10 flashcards about Python (array format) |
| `data/science_facts.json` | **Create** | 8 flashcards about science (object `{"cards": [...]}` format) |
| `tests/test_flashcard_loader.py` | **Create** | 9+ tests covering valid loading, error handling, security |
| `tests/conftest.py` | **Create** | Shared fixtures (`sample_deck`, `single_card_deck`) |

## TDD Task List

Write these tests FIRST (they must fail against stubs):

1. `test_load_valid_flashcards_array` — array format `[{"front": ..., "back": ...}]` loads correctly
2. `test_load_valid_flashcards_object_format` — `{"cards": [...]}` format loads correctly
3. `test_load_invalid_json_raises_system_exit` — malformed JSON triggers `SystemExit`
4. `test_load_missing_back_field_raises` — card without `"back"` triggers `SystemExit`
5. `test_load_missing_front_field_raises` — card without `"front"` triggers `SystemExit`
6. `test_load_empty_deck_raises` — empty array `[]` triggers `SystemExit`
7. `test_load_nonexistent_file_raises` — missing file triggers `SystemExit`
8. `test_path_traversal_rejected` — `../../etc/passwd` triggers `SystemExit` (friendly message); also test `_validate_path()` directly for `ValueError`
9. `test_oversized_file_rejected` — file > 10 MB triggers `SystemExit`

## Security Considerations

| Threat | Mitigation |
|--------|-----------|
| Path traversal (`../../etc/passwd`) | `_validate_path()` anchored to project dir via `__file__` |
| Oversized files (DoS) | `os.path.getsize()` pre-check + read with byte cap |
| Malformed JSON injection | `json.loads()` inside `try/except json.JSONDecodeError` |
| Missing required fields | Explicit `"front"` and `"back"` key validation |
| Non-list/dict JSON root | Type check after parse, reject other types |

## Acceptance Criteria

- [ ] `load_flashcards("data/python_basics.json")` returns 10 `FlashCard` objects
- [ ] `load_flashcards("data/science_facts.json")` returns 8 `FlashCard` objects
- [ ] All 9 tests pass with `pytest tests/test_flashcard_loader.py -v`
- [ ] `flake8 data_loader.py utils/file_handler.py` returns zero errors
- [ ] `mypy data_loader.py utils/file_handler.py --ignore-missing-imports` returns zero errors
- [ ] Error messages follow the format: `Error: <msg> in "<file>" / Hint: <fix>`

## Risks

| Risk | Mitigation |
|------|-----------|
| Starter's `FileHandler` class used by starter tests | Existing `tests/test_file_handler.py` and `tests/test_task_manager.py` test the old starter code; they will be replaced in later phases |
| `SAFE_BASE_DIR` incorrect during tests | Use `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` not `os.getcwd()` |
| Python 3.9 incompatible type syntax | Use `from __future__ import annotations` in all modules |
