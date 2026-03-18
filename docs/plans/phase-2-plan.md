# Phase 2 — Quiz Engine (Strategy + Factory Pattern)

## Objective
Implement the quiz engine with three modes (Sequential, Random, Adaptive) using
the Strategy Pattern, a Factory for mode selection, and a QuizSession orchestrator
that tracks answers and computes stats.

## Files to create/modify

| File | Action | Description |
|------|--------|-------------|
| `quiz_engine.py` | **Create** | QuizMode ABC, SequentialMode, RandomMode, AdaptiveMode, QuizModeFactory, SessionStats, QuizSession |
| `tests/test_quiz_modes.py` | **Create** | 13 tests covering factory, modes, session stats, answer matching |

## TDD Task List

1. `test_factory_returns_sequential_mode` — factory creates SequentialMode
2. `test_factory_returns_random_mode` — factory creates RandomMode
3. `test_factory_returns_adaptive_mode` — factory creates AdaptiveMode
4. `test_factory_case_insensitive` — `"SEQUENTIAL"` works
5. `test_factory_raises_for_unknown_mode` — `"badmode"` raises ValueError
6. `test_sequential_exhausts_deck_in_order` — cards returned 1..N then None
7. `test_random_mode_returns_all_cards_no_repeats` — all cards, no duplicates
8. `test_adaptive_mode_repeats_missed_cards` — missed cards reappear
9. `test_adaptive_mode_ends_only_when_all_correct` — ends after all correct
10. `test_session_stats_accuracy_calculation` — accuracy = correct/total * 100
11. `test_answer_is_case_insensitive` — "PYTHON" matches "python"
12. `test_answer_strips_leading_trailing_whitespace` — "  python  " matches "python"
13. `test_session_tracks_missed_cards_correctly` — missed_cards list accurate

## Security Considerations

| Threat | Mitigation |
|--------|-----------|
| Infinite loop in AdaptiveMode | Cap retries at `len(deck) * 3` |
| Empty deck passed to mode | Validate deck non-empty in QuizSession constructor |

## Acceptance Criteria

- [ ] All 13 tests pass
- [ ] `flake8 quiz_engine.py` zero errors
- [ ] `mypy quiz_engine.py --ignore-missing-imports` zero errors
- [ ] Strategy Pattern: QuizMode ABC with 3 concrete implementations
- [ ] Factory Pattern: QuizModeFactory.create() with case-insensitive lookup
- [ ] SessionStats.accuracy is a computed @property

## Risks

| Risk | Mitigation |
|------|-----------|
| Random mode test flakiness | Test set equality not order; seed if needed |
| Adaptive mode complexity | Clear state machine: wrong→re-queue, right→remove |
