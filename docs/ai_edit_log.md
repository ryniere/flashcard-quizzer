# AI Edit Log

This document records real interactions with Claude Code during the development
of Flashcard Quizzer. Each entry corresponds to one project phase and captures
the prompt given, the problem found in the AI output, and the human-driven fix
that followed.

---

## Entry 1 — Phase 1: Data Layer

**Date:** 2026-03-18

**Prompt used:** "Implement utils/file_handler.py with _validate_path() and read_file()"

**AI Response Summary:** Claude Code generated a `FileHandler` class with a
private `_validate_path()` method that checked whether a given file path began
with the expected base directory using `str.startswith()`. The `read_file()`
method opened JSON files, parsed them, and returned a list of raw card
dictionaries.

**Issue found in AI output:** The `startswith()` check is not a secure directory
containment guard. A path like `/data-evil/malicious.json` passes validation
when the base directory is `/data` because the string prefix matches. This is a
classic path-traversal weakness.

**Fix applied:** Replaced `startswith()` with `os.path.commonpath()` to perform
a proper directory containment check. Then, during a second review pass,
wrapped the target path with `os.path.realpath()` before comparison so that
symlinks pointing outside the allowed directory are also caught.

**Lesson learned:** String prefix comparison is not a secure directory
containment check. Always resolve paths to their canonical form and use
filesystem-aware comparison functions.

---

## Entry 2 — Phase 2: Quiz Engine

**Date:** 2026-03-18

**Prompt used:** "Implement quiz_engine.py with Strategy Pattern + Factory"

**AI Response Summary:** Claude Code produced a `QuizEngine` class backed by a
Strategy Pattern for answer-checking (case-insensitive, strict, partial match)
and a Factory that instantiated the correct strategy from a string key. The
engine tracked missed cards in a list using `not in` to avoid duplicates.

**Issue found in AI output:** The `missed_cards` deduplication relied on
`not in`, which uses value equality (`__eq__`). Because `FlashCard` is a
dataclass with default equality, two distinct card objects with the same
question and answer text are considered equal. If the deck contains intentional
duplicates (e.g., the same term in different categories), the engine undercounts
misses.

**Fix applied:** Switched from a list with `not in` to a `_missed_ids: set[int]`
that stores `id()` values of missed card objects. The public `missed_cards`
property reconstructs the list by filtering the deck against the ID set.

**Lesson learned:** Dataclass value equality can cause subtle bugs when tracking
object identity matters. Use `id()` or explicit unique keys when you need to
distinguish objects that may share field values.

---

## Entry 3 — Phase 3: UI Layer

**Date:** 2026-03-18

**Prompt used:** "Create ui.py with colored terminal output and input handling"

**AI Response Summary:** Claude Code built a `TerminalUI` class that wrapped
`input()` calls with colorama-based ANSI formatting. It displayed cards, read
answers, and showed score summaries. The main input loop was wrapped in a
`try/except KeyboardInterrupt` to handle Ctrl+C gracefully.

**Issue found in AI output:** The code only caught `KeyboardInterrupt` but
ignored `EOFError`. When standard input is closed (Ctrl+D on Unix, Ctrl+Z on
Windows, or piped stdin reaching end-of-file), Python raises `EOFError`, not
`KeyboardInterrupt`. This caused an unhandled exception and a raw traceback
instead of a clean exit.

**Fix applied:** Added `EOFError` to the `except` clause alongside
`KeyboardInterrupt`, so both termination signals produce a friendly "Quiz
ended" message and a clean exit.

**Lesson learned:** Always handle all stdin termination signals, not just
Ctrl+C. Any code that calls `input()` in a loop must catch both
`KeyboardInterrupt` and `EOFError`.

---

## Entry 4 — Phase 4: Entry Point

**Date:** 2026-03-18

**Prompt used:** "Implement main.py with argparse CLI wiring all modules"

**AI Response Summary:** Claude Code generated a `main()` function that used
`argparse` to accept a flashcard file path and quiz options, then instantiated
`FileHandler`, `QuizEngine`, and `TerminalUI`, wiring them together in a quiz
loop. Each module handled its own domain-specific exceptions internally.

**Issue found in AI output:** Despite each module having its own error handling,
unexpected exceptions in the quiz loop (e.g., a corrupted card triggering a
`TypeError` deep in the strategy) would still leak raw tracebacks to the
terminal. There was no top-level safety net.

**Fix applied:** Added a broad `except Exception` around the quiz loop in
`main()` that logs the error message, prints a user-friendly "Something went
wrong" notice, and exits with a non-zero code. This sits outside the
module-level handlers as a last resort.

**Lesson learned:** A top-level catch-all is needed even when inner modules
handle their own errors. The entry point is the last line of defense against
ugly tracebacks reaching the user.

---

## Entry 5 — Phase 5: Test Hardening

**Date:** 2026-03-18

**Prompt used:** "Add edge case tests for comprehensive coverage"

**AI Response Summary:** Claude Code created a new test file with parametrized
edge-case tests covering empty decks, single-card decks, unicode content,
and malformed JSON input. The tests used pytest fixtures and covered branches
that the initial test suite missed.

**Issue found in AI output:** The new test file contained no type annotations on
any function. The project's `pyproject.toml` sets `disallow_untyped_defs = true`
in the mypy configuration, so every function — including test functions — must
have a return type annotation. Running `mypy` on the new file produced dozens
of errors.

**Fix applied:** Added `-> None` return type annotations to every test function.
For tests that used optional fixture values, added explicit `assert x is not
None` narrowing statements before use so mypy could verify type safety.

**Lesson learned:** Even test files must respect the project's typing
configuration. When `disallow_untyped_defs` is enabled, there are no exceptions
for test code.

---

## Entry 6 — Phase 6: Configuration

**Date:** 2026-03-18

**Prompt used:** "Refine .flake8, pyproject.toml, pytest.ini for CI enforcement"

**AI Response Summary:** Claude Code updated the linter and test configuration
files to enforce stricter quality gates. It set the pytest-cov
`fail_under = 80` threshold, tightened flake8 line-length rules, and aligned
mypy settings across all packages.

**Issue found in AI output:** The `fail_under = 80` setting does not enforce
"greater than 80%" coverage. Pytest-cov treats this as "greater than or equal
to," meaning a run that hits exactly 80.0% passes. The project requirement was
strictly above 80%.

**Fix applied:** Changed `fail_under` from `80` to `81`. This guarantees that
any coverage result at or below 80.0% fails the check, which matches the
intended "greater than 80%" requirement.

**Lesson learned:** Off-by-one errors appear in configuration, not just code.
"Greater than 80" means the threshold must be set to 81 when the tool uses
greater-than-or-equal semantics.

---

## Entry 7 — Phase 7: Documentation

**Date:** 2026-03-18

**Prompt used:** "Create README.md, ai_edit_log.md, final report, prompts.md"

**AI Response Summary:** Claude Code generated a full README with badges, a
quick-start section, usage instructions, and a contributing guide. It also
scaffolded this AI edit log, the final report, and the prompts reference
document.

**Issue found in AI output:** The initial README described every module in prose
but lacked a visual architecture diagram. Without a structural overview,
readers had to mentally reconstruct the module relationships from paragraphs of
text — exactly the kind of cognitive load a diagram eliminates.

**Fix applied:** Added an ASCII architecture diagram to the README showing the
dependency flow between `main.py`, `quiz_engine.py`, `ui.py`,
`file_handler.py`, and the data directory. The diagram uses box-drawing
characters and clearly labels each module's responsibility.

**Lesson learned:** Architecture diagrams make the codebase much more
approachable for reviewers. A 10-line ASCII diagram can replace several
paragraphs of structural description and is far easier to scan.

---

## Summary Statistics

- **Total AI interactions:** 7 (one per project phase)
- **AI tool used:** Claude Code
- **Most common issue category:** Edge-case handling and off-by-one semantics
- **Most impactful fix:** Phase 1 path validation (security)
- **Most subtle fix:** Phase 2 identity vs. equality tracking
- **Biggest lesson learned:** AI-generated code consistently handles the happy
  path well but requires human review for security boundaries, edge cases, and
  configuration semantics
