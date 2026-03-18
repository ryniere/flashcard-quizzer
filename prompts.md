# Prompt Evolution Log

This document traces how prompts were refined across all seven phases of the
Flashcard Quizzer project. Each phase used Claude Code with subagents, followed
a strict TDD workflow (red-green-refactor), and incorporated feedback from pull
request reviews to drive prompt improvements.

---

## Phase 1 -- Data Layer

**Initial prompt:**
"Implement `utils/file_handler.py` with `_validate_path()` and `read_file()`,
plus `data_loader.py` with a `FlashCard` dataclass and `load_flashcards()`.
Support both JSON array and `{"cards": [...]}` formats. Follow the TDD task
list in `docs/plans/phase-1-plan.md`."

**Refinement after seeing output:**
The first implementation used `os.path.abspath()` for path resolution, but the
PR review identified that symlinks could bypass the containment check. The
prompt was refined to specify: "Use `os.path.realpath()` to resolve symlinks
before comparing against `SAFE_BASE_DIR`, and also apply `realpath()` when
computing `SAFE_BASE_DIR` itself." Additionally, the initial `_validate_path()`
used `str.startswith()` for the containment check, which a sibling directory
like `/home/project-evil` could defeat if `SAFE_BASE_DIR` were `/home/project`.
The prompt was updated to require `os.path.commonpath()` instead.

**Key learning:**
Security-related prompts need to be extremely specific. A vague instruction
like "validate the path" produces code that looks correct at first glance but
fails adversarial test cases. Spelling out the exact mechanism
(`realpath` + `commonpath`) produced hardened output on the first try.

---

## Phase 2 -- Quiz Engine

**Initial prompt:**
"Create `quiz_engine.py` implementing the Strategy Pattern with `QuizMode` ABC
and three concrete modes (`SequentialMode`, `RandomMode`, `AdaptiveMode`), plus
a `QuizModeFactory` and `QuizSession` orchestrator. Write all 13 tests from
the phase-2 plan first, confirm they fail, then implement."

**Refinement after seeing output:**
The AI initially compared answers using `==` (value equality), which meant two
`FlashCard` objects with identical `front`/`back` text would collide when
tracking missed cards. The PR review flagged this: if a deck contains
duplicate-valued cards, the missed-card list under-counts. The prompt was
refined to add: "Track missed cards by object identity (`id(card)`) to
distinguish duplicate-valued cards." A regression test
(`test_missed_cards_tracks_duplicates_by_identity`) was added to lock this fix.

A second refinement addressed AdaptiveMode: the initial implementation had no
retry cap, creating the potential for an infinite loop if a user always answers
incorrectly. The prompt was updated to specify: "Cap total serves at
`len(deck) * 3` and expose a `was_force_stopped` property."

**Key learning:**
Identity vs. equality is a subtle distinction that AI tends to default
conservatively on (using `==`). Prompts that involve collections of objects
should state whether identity or equality semantics are intended. Also,
unbounded loops are a class of bug that AI rarely self-detects -- the prompt
must anticipate and cap them.

---

## Phase 3 -- UI Layer

**Initial prompt:**
"Build `ui.py` with `display_card()`, `get_user_answer()`,
`display_feedback()`, `display_stats()`, and `display_welcome()`. Use colorama
for colors. Do NOT call `colorama.init()` in `ui.py` -- it belongs in
`main.py`. Write the 7 TDD tests from the phase-3 plan first."

**Refinement after seeing output:**
The first implementation of `get_user_answer()` caught `KeyboardInterrupt` to
handle Ctrl+C but did not catch `EOFError`. When stdin is piped (common in
automated testing and CI), reaching end-of-file raises `EOFError`, which
crashed the application with a raw traceback. The PR review caught this, and
the prompt was refined to: "Catch both `KeyboardInterrupt` and `EOFError` in
`get_user_answer()`, converting both to `SystemExit(0)`." A corresponding
regression test (`test_eof_raises_system_exit`) was added.

**Key learning:**
Interactive CLI applications need to handle three exit paths: explicit command
(`exit`), keyboard interrupt (Ctrl+C), and EOF (Ctrl+D / piped stdin). If the
prompt only mentions two, the AI will only implement two. Exhaustively listing
expected signals in the prompt prevented this class of bug in later phases.

---

## Phase 4 -- Entry Point

**Initial prompt:**
"Rewrite `main.py` as the CLI entry point with argparse. Wire together
`data_loader`, `quiz_engine`, and `ui` into a complete interactive session.
Arguments: `-f`/`--file` (required), `-m`/`--mode` (default: sequential),
`--stats`, `--version`. All exceptions must be caught at the top level -- the
user must never see a Python traceback."

**Refinement after seeing output:**
The initial `run()` function caught `SystemExit` but re-raised it immediately,
which worked for `load_flashcards` errors. However, the quiz loop itself could
raise `SystemExit(0)` when the user typed `exit`, and the initial code did not
display session stats before exiting in that case. The prompt was refined to:
"Catch `SystemExit` inside the quiz loop and fall through to stats display,
so the user always sees their results even when quitting early."

A second refinement added handling for the AdaptiveMode retry cap: "If
`AdaptiveMode.was_force_stopped` is True after the loop, print a warning
explaining that the session ended early due to the retry limit."

The PR review also flagged that an uncaught generic `Exception` in the quiz
loop would print a traceback. The prompt was updated to add a broad
`except Exception` inside the loop that logs details to stderr and prints a
friendly message to stdout.

**Key learning:**
Entry-point orchestration is where all edge cases converge. Prompts for this
layer need to enumerate every exit scenario (clean finish, user exit, Ctrl+C,
unexpected error, retry cap) and state what the user should see in each case.
A table-driven specification in the prompt ("If X happens, the user sees Y")
produced more reliable output than a paragraph of prose.

---

## Phase 5 -- Test Suite Hardening

**Initial prompt:**
"Add edge case tests to close coverage gaps. Current state: 52 tests, 96%
coverage. Target: 64+ tests, 99%+ coverage. Add the 7 tests specified in
the phase-5 plan, plus any additional tests needed to cover uncovered lines.
Refer to the coverage report for missing lines."

**Refinement after seeing output:**
The AI generated the 7 specified tests, but coverage only reached 97% because
three branches remained untested: (1) the `commonpath` ValueError path in
`_validate_path()` (Windows cross-drive scenario), (2) the TOCTOU race
condition where a file disappears between `os.path.getsize()` and `open()`,
and (3) the generic `Exception` handler in `main.run()`. The prompt was
refined with explicit instructions: "Add tests for these specific uncovered
branches: `file_handler.py:35-37` (mock `os.path.commonpath` to raise
`ValueError`), `file_handler.py:77-78` (mock `builtins.open` to raise
`FileNotFoundError`), `main.py:59-61` (mock `load_flashcards` to raise
`RuntimeError`)."

A further refinement addressed a mypy error in the concurrent sessions test
where the return type of `next_card()` included `None`, requiring an explicit
`assert c1 is not None` guard before calling `c1.back`.

**Key learning:**
Asking the AI to "close coverage gaps" is too vague. Providing the exact file
and line numbers, along with the specific mock needed, produced targeted tests
that hit the right branches on the first attempt. Coverage-driven testing
prompts should always reference the coverage report output directly.

---

## Phase 6 -- Configuration Refinement

**Initial prompt:**
"Review and finalize `.flake8`, `pyproject.toml`, and `pytest.ini`. Add
`[tool.coverage.report] fail_under = 80` to enforce minimum coverage in CI.
Ensure the full verification suite passes: pytest + flake8 + mypy."

**Refinement after seeing output:**
The AI initially added `W503` to the flake8 `extend-ignore` list, which is
deprecated in flake8 6.x and caused a warning. The prompt was refined to
explicitly state: "Do NOT ignore W503 -- it is deprecated in flake8 6.x."

A second refinement set `fail_under = 81` instead of `80` to provide a buffer
above the Udacity minimum. The AI also added `check_untyped_defs = true` to
the mypy configuration for tests, which the prompt had not originally
requested but improved type safety.

**Key learning:**
Configuration prompts benefit from including the tool version as context. The
AI's training data includes patterns from older versions of flake8 where W503
was valid. Stating the version prevents the AI from applying outdated
configuration patterns.

---

## Phase 7 -- Documentation

**Initial prompt:**
"Create all required documentation: (1) Rewrite README.md with all 10 required
sections including architecture diagram, design patterns, security notes.
(2) Rewrite `docs/ai_edit_log.md` with 7 genuine interaction entries, one per
phase. (3) Create `docs/final_report_template.md` as the final project report
(1000-1500 words). (4) Create `prompts.md` documenting prompt evolution across
all 7 phases."

**Refinement after seeing output:**
The initial README draft included emojis in section headers, which conflicted
with the project's plain-text terminal aesthetic. The prompt was refined to:
"Use ASCII text only for headers and decorative elements -- no emoji in
headings." The architecture diagram was also refined from a simple list to an
ASCII box diagram showing module dependencies and data flow.

For the AI edit log, the initial output was generic. The prompt was refined to
require: "Each entry must reference a specific commit hash, cite the exact
prompt that was used, describe the exact bug that was found, and explain the
exact fix. No fabricated entries."

**Key learning:**
Documentation prompts produce better output when they include constraints on
style (no emoji), format (ASCII diagrams), and content quality (specific
commit references). Without these constraints, the AI defaults to a generic,
marketing-style tone that does not match a technical project.

---

## Cross-Phase Patterns

### What worked consistently
- **Providing the TDD task list in the prompt** -- When the prompt included the
  exact test names and descriptions, the AI produced tests that matched the
  specification on the first attempt.
- **Referencing plan files** -- Directing the AI to "read
  `docs/plans/phase-N-plan.md` first" gave it the architectural context needed
  to produce implementation code consistent with the design.
- **Using subagents for parallel implementation** -- Dispatching separate
  subagents for separate modules (e.g., `file_handler.py` and `data_loader.py`)
  produced focused, well-scoped code with fewer unintended side effects.

### What required repeated correction
- **Security edge cases** -- The AI consistently produced code that passed
  happy-path tests but missed adversarial inputs (symlinks, sibling directories,
  TOCTOU races). Explicit adversarial test cases in the prompt were the only
  reliable mitigation.
- **Exit path completeness** -- The AI would handle 2 of 3 exit signals unless
  all three were enumerated in the prompt.
- **Tool version awareness** -- Deprecated flags and options appeared in AI
  output unless the prompt specified the tool version.
