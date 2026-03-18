# Phase 4 — Entry Point (CLI with argparse)

## Objective
Build `main.py` as the CLI entry point with argparse, wiring together
data_loader, quiz_engine, and ui into a complete interactive quiz session.

## Files to modify

| File | Action | Description |
|------|--------|-------------|
| `main.py` | **Rewrite** | Replace placeholder with argparse CLI + run() orchestrator |
| `tests/test_integration.py` | **Create** | 6 integration tests for CLI behavior |

## TDD Task List

1. `test_main_requires_file_argument` — missing `-f` → non-zero exit
2. `test_main_default_mode_is_sequential` — no `-m` → sequential
3. `test_main_invalid_mode_exits_cleanly` — `-m badmode` → SystemExit with message
4. `test_main_nonexistent_file_exits_cleanly` — missing file → friendly message
5. `test_main_smoke_sequential` — full run with mocked input, 3 answers
6. `test_main_smoke_adaptive` — full run in adaptive mode with mocked input

## Design Notes

- `colorama.init(autoreset=True)` called at top of main.py
- `__version__ = "1.0.0"` defined in main.py
- All exceptions caught at top level in run() — no tracebacks to user
- Verbose errors logged to stderr, friendly messages to stdout

## Acceptance Criteria

- [ ] All 6 tests pass
- [ ] flake8 + mypy zero errors
- [ ] `echo "exit" | python main.py -f data/python_basics.json` exits cleanly
