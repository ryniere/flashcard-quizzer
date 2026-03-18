# Phase 5 — Test Suite Hardening

## Objective
Add edge case tests, cover remaining gaps, ensure >80% coverage (target ≥85%).

## Current state
- 52 tests passing, 96% coverage
- Missing lines: data_loader.py:65, main.py:59-61/82/99, file_handler.py:35-37/77-78

## Additional tests (from spec)

1. `test_load_json_with_extra_fields_is_accepted` — extra keys in card dict ignored
2. `test_sequential_with_single_card` — deck of 1
3. `test_adaptive_with_all_wrong_then_all_correct` — full retry cycle
4. `test_stats_with_zero_questions` — SessionStats with total=0
5. `test_answer_with_unicode_input` — Unicode answer handled safely
6. `test_file_path_with_spaces` — path with spaces works
7. `test_concurrent_sessions_independent` — two sessions don't share state
