# Phase 3 — UI Layer

## Objective
Build the terminal UI with colored output, user input handling, stats display,
and graceful exit on `exit` command or `Ctrl+C`.

## Files to create

| File | Action | Description |
|------|--------|-------------|
| `ui.py` | **Create** | display_card, get_user_answer, display_feedback, display_stats, display_welcome |
| `tests/test_ui.py` | **Create** | 7 tests covering output, input, and exit handling |

## TDD Task List

1. `test_display_card_outputs_front` — stdout contains card front text
2. `test_display_feedback_correct` — correct answer shows green feedback
3. `test_display_feedback_incorrect` — wrong answer shows red + expected
4. `test_display_stats_shows_all_fields` — summary has accuracy, total, correct
5. `test_get_user_answer_strips_whitespace` — leading/trailing space removed
6. `test_exit_command_raises_system_exit` — typing "exit" raises SystemExit(0)
7. `test_keyboard_interrupt_raises_system_exit` — Ctrl+C raises SystemExit(0)

## Design Notes

- colorama.init() is called in main.py (Phase 4), NOT in ui.py
- All output functions are pure — testable with capsys
- get_user_answer validates: strip whitespace, enforce max 500 chars
- Input truncated at 500 chars (no error, just truncated)

## Acceptance Criteria

- [ ] All 7 tests pass
- [ ] flake8 zero errors
- [ ] mypy zero errors
- [ ] Output uses colorama Fore.GREEN/RED for feedback
