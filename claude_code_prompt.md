# Claude Code Prompt — Flashcard Quizzer CLI
# Professional Engineering Workflow

> Copy everything below this line and paste into Claude Code.

---

## CONTEXT

You are a senior Python software engineer operating under strict engineering discipline. You will build a complete, production-quality **Flashcard Quizzer CLI application** based on the Udacity project starter at:
`https://github.com/udacity/cd14602-project-starter/tree/main/project`

Target repository: `https://github.com/ryniere/flashcard-quizzer`

---

## MANDATORY WORKFLOW — MUST FOLLOW FOR EVERY PHASE

Every phase (1 through 7) **must** follow this exact sequence. Do not skip any step.

```
┌─────────────────────────────────────────────────────────────┐
│  FOR EACH PHASE:                                            │
│                                                             │
│  1. PLAN        → Write a detailed implementation plan      │
│  2. REVIEW      → Run /review on the plan (code review)     │
│  3. BRANCH      → Create a git feature branch               │
│  4. TDD         → Write failing tests FIRST                 │
│  5. IMPLEMENT   → Use subagents to implement the code       │
│  6. VERIFY      → Run tests + linting, all must pass        │
│  7. PR          → Open a Pull Request to main               │
└─────────────────────────────────────────────────────────────┘
```

### Step 1 — PLAN (before writing any code)
Write a markdown plan file at `docs/plans/phase-N-plan.md` containing:
- **Objective**: what this phase accomplishes
- **Files to create/modify**: list every file with a one-line description
- **TDD task list**: each test to write, before writing implementation
- **Security considerations**: threats and mitigations for this phase
- **Acceptance criteria**: how to know the phase is done
- **Risks**: what could go wrong and how to handle it

### Step 2 — REVIEW (plan review before coding)
After writing the plan, run:
```
/review docs/plans/phase-N-plan.md
```
Address every finding from the review before proceeding. If the review raises concerns, update the plan. Do not proceed to coding until the plan is approved (no blockers).

### Step 3 — BRANCH (git feature branch)
Create a dedicated branch for each phase:
```bash
git checkout main
git pull origin main
git checkout -b feat/phase-N-<short-description>
```
Branch naming convention:
- `feat/phase-1-data-layer`
- `feat/phase-2-quiz-engine`
- `feat/phase-3-ui-layer`
- `feat/phase-4-entry-point`
- `feat/phase-5-test-suite`
- `feat/phase-6-config`
- `feat/phase-7-documentation`

### Step 4 — TDD (tests before implementation)
**Write ALL tests for the phase FIRST. They must fail (red). Then implement the code to make them pass (green). Then refactor (refactor).**

This is not optional. Red → Green → Refactor is the law.

**Step 4a — Create stub modules first:**
Before writing tests, create skeleton module files with stub implementations so that tests can import them without `ImportError`. Each function should raise `NotImplementedError`:
```python
# Example stub for data_loader.py
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class FlashCard:
    front: str
    back: str

def load_flashcards(filepath: str) -> list[FlashCard]:
    raise NotImplementedError
```

**Step 4b — Write tests:**
Use subagents to write tests:
```
Use a subagent to write the test file tests/test_<module>.py
following the TDD task list in docs/plans/phase-N-plan.md.
The tests must be complete and runnable but will fail until
implementation is provided. Do not write any implementation yet.
```

Confirm tests fail: `pytest tests/test_<module>.py` must show **failures** (not collection errors). The stubs ensure modules are importable, so pytest can collect and run tests that fail against `NotImplementedError` or incorrect return values.

### Step 5 — IMPLEMENT (subagent execution)
Dispatch subagents to implement each module independently:
```
Dispatch parallel subagents:
- Subagent A: implement <module1>.py to pass its tests
- Subagent B: implement <module2>.py to pass its tests
Each subagent must run pytest on its own module before completing.
```

Each subagent must:
1. Read the plan file first
2. Read the failing test file first
3. Write implementation to pass the tests
4. Run `pytest tests/test_<module>.py -v` and confirm all pass
5. Run `flake8 <module>.py` and confirm zero errors

### Step 6 — VERIFY (quality gates — all must pass)
Before creating the PR, run ALL of the following. All must pass:
```bash
pytest --cov=. --cov-report=term-missing   # >80% coverage (Udacity minimum), aim for ≥85%
flake8 .                                    # zero errors
python -m mypy . --ignore-missing-imports  # zero type errors
echo -e "answer\nanswer\nexit" | python main.py -f data/python_basics.json -m sequential  # smoke test (piped input)
```
If any gate fails, fix it before creating the PR. Do not create a PR with failing gates.

**Note:** The smoke test uses piped input to avoid blocking on interactive input. Adjust the answers as needed.

### Step 7 — PR (Pull Request)
After all gates pass, push the branch and open a PR:
```bash
git add <list specific files changed in this phase>
git commit -m "feat(phase-N): <description> [TDD, Strategy Pattern, security hardened]"
git push -u origin feat/phase-N-<short-description>
gh pr create \
  --base main \
  --title "Phase N: <Phase Title>" \
  --body "## Summary
- <bullet 1>
- <bullet 2>

## TDD Evidence
- Tests written first: ✅
- All tests passing: ✅
- Coverage: XX%

## Security Checklist
- [ ] Input validated
- [ ] No path traversal possible
- [ ] No raw tracebacks exposed
- [ ] No hardcoded secrets

## Quality Gates
- flake8: ✅ zero errors
- mypy: ✅ zero errors
- pytest: ✅ all passing
- Coverage: >80% ✅ (target: ≥85%)"
```

---

## PHASE 0 — REPOSITORY SETUP (no PR needed for this phase)

1. Copy the Udacity starter files into the project directory:
   ```bash
   git clone https://github.com/udacity/cd14602-project-starter.git /tmp/udacity-starter
   cp -r /tmp/udacity-starter/project/* .
   cp -r /tmp/udacity-starter/project/.* . 2>/dev/null || true
   rm -rf /tmp/udacity-starter
   ```

2. Initialize fresh repo pointing to the GitHub remote:
   ```bash
   git init
   git remote add origin https://github.com/ryniere/flashcard-quizzer.git
   ```

3. Create `main` as the default protected branch (all feature work goes in PRs).

4. Create `.gitignore` (Python):
   ```
   __pycache__/
   *.pyc
   *.pyo
   .pytest_cache/
   htmlcov/
   .coverage
   .env
   *.egg-info/
   dist/
   build/
   .mypy_cache/
   .DS_Store
   .vscode/
   .idea/
   venv/
   .venv/
   *.swp
   ```

5. Create `requirements.txt` with exact pinned versions:
   ```
   pytest==7.4.4
   pytest-cov==4.1.0
   coverage==7.4.0
   colorama==0.4.6
   flake8==6.1.0
   mypy==1.8.0
   ```

6. Create `docs/plans/` directory (used by all phases).

7. Create `utils/__init__.py` (empty file, required for package imports).

8. Create `.flake8` configuration file (flake8 does NOT read `pyproject.toml` natively):
   ```ini
   [flake8]
   max-line-length = 99
   extend-ignore = E203
   exclude = .git,__pycache__,htmlcov,venv,.venv
   ```

9. Create `pyproject.toml` (mypy + coverage config):
   ```toml
   [tool.mypy]
   python_version = "3.11"
   strict = false
   ignore_missing_imports = true
   disallow_untyped_defs = true
   warn_return_any = true
   warn_unused_ignores = true

   [tool.coverage.run]
   omit = ["tests/*"]
   ```

10. Create `pytest.ini`:
    ```ini
    [pytest]
    testpaths = tests
    addopts = --cov=. --cov-report=term-missing
    ```

11. Initial commit and push:
    ```bash
    git add .gitignore requirements.txt pytest.ini pyproject.toml .flake8 utils/__init__.py docs/
    git commit -m "chore: initialize project from Udacity starter with tooling"
    git push -u origin main
    ```

Do NOT delete the existing folder structure from the starter (`data/`, `utils/`, `tests/`, `docs/`).

**IMPORTANT**: All Python modules in this project must include `from __future__ import annotations` as the first import. This ensures PEP 604 union syntax (`X | None`) and PEP 585 generics (`list[str]`) work on Python 3.9+.

---

## FINAL PROJECT STRUCTURE

```
flashcard-quizzer/
├── main.py                      # CLI entry point — argparse
├── quiz_engine.py               # Strategy + Factory pattern
├── data_loader.py               # JSON loading & validation
├── ui.py                        # Terminal I/O, colors, stats
├── data/
│   ├── python_basics.json       # Sample deck (array format)
│   └── science_facts.json       # Sample deck (object format)
├── utils/
│   ├── __init__.py
│   └── file_handler.py          # Low-level file read helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_flashcard_loader.py
│   ├── test_quiz_modes.py
│   └── test_integration.py
├── docs/
│   ├── plans/
│   │   ├── phase-1-plan.md
│   │   ├── phase-2-plan.md
│   │   └── ...
│   ├── ai_edit_log.md
│   └── final_report_template.md
├── prompts.md
├── README.md
├── requirements.txt
├── pytest.ini
├── pyproject.toml               # mypy + coverage config
├── .flake8                      # flake8 config (flake8 does NOT read pyproject.toml)
└── .gitignore
```

---

## SECURITY REQUIREMENTS (apply to every phase)

These are non-negotiable. Enforce them in every module:

### Input Validation
- Validate ALL user-provided strings before use (strip whitespace, enforce max length of 500 chars).
- Reject answers that are not printable ASCII/UTF-8.
- Validate file paths before opening: reject paths with `..`, null bytes, or absolute paths outside the working directory.

### Path Traversal Prevention
In `utils/file_handler.py`:
```python
from __future__ import annotations
import os

# Anchored to the file's location, not the process's cwd (which varies in tests)
SAFE_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _validate_path(filepath: str) -> str:
    """Raise ValueError if filepath escapes the project directory."""
    resolved = os.path.abspath(filepath)
    if not resolved.startswith(SAFE_BASE_DIR):
        raise ValueError(f"Unsafe file path: '{filepath}' is outside the allowed directory.")
    return resolved
```
Call `_validate_path()` before every `open()` call. The `load_flashcards()` function should catch `ValueError` from `_validate_path()` and convert it to `SystemExit` with a friendly message, keeping error handling consistent.

### No Secrets in Code
- No hardcoded credentials, tokens, or API keys anywhere.
- `.env` is in `.gitignore`.

### Safe Error Messages
- Never expose internal file paths, stack traces, or system information to the user.
- Log verbose errors to stderr, show friendly messages to stdout.

### JSON Parsing Safety
- Use `json.loads()` inside a `try/except json.JSONDecodeError`.
- Reject JSON files larger than 10 MB. **Preferred approach:** read the file in chunks with a byte limit rather than using `os.path.getsize()` (which is susceptible to TOCTOU race conditions). Alternatively, use `os.path.getsize()` as a quick pre-check, but read with a size cap as the authoritative limit.
- Validate that parsed JSON is either a `list` or a `dict` — reject any other type.

---

## PHASE 1 — DATA LAYER

> Follow the 7-step mandatory workflow. Branch: `feat/phase-1-data-layer`

### TDD Task List (write tests first):
1. `test_load_valid_flashcards_array` — array format loads correctly
2. `test_load_valid_flashcards_object_format` — `{"cards": [...]}` loads correctly
3. `test_load_invalid_json_raises_system_exit` — malformed JSON → `SystemExit`
4. `test_load_missing_back_field_raises` — card without `"back"` → `SystemExit`
5. `test_load_missing_front_field_raises` — card without `"front"` → `SystemExit`
6. `test_load_empty_deck_raises` — empty array → `SystemExit`
7. `test_load_nonexistent_file_raises` — missing file → `SystemExit`
8. `test_path_traversal_rejected` — `../../etc/passwd` → `SystemExit` (friendly message). Also test `_validate_path()` directly for `ValueError`.
9. `test_oversized_file_rejected` — file > 10 MB → `SystemExit`

### `utils/file_handler.py`
```python
def read_file(path: str) -> str:
    """Read file safely after path validation and size check."""
```

### `data_loader.py`
```python
from __future__ import annotations

@dataclass
class FlashCard:
    front: str
    back: str

def load_flashcards(filepath: str) -> list[FlashCard]:
    """Load and validate flashcards from a JSON file.

    Supports array format and object {"cards": [...]} format.
    Raises SystemExit with a user-friendly message on any error.
    """
```

Error messages must always follow this format (friendly, no traceback):
```
❌ Error: <what went wrong> in "<filename>"
   Hint: <how to fix it>
```

### Sample JSON files
- `data/python_basics.json`: 10 cards about Python (array format)
- `data/science_facts.json`: 8 cards about science (`{"cards": [...]}` format)

---

## PHASE 2 — QUIZ ENGINE

> Follow the 7-step mandatory workflow. Branch: `feat/phase-2-quiz-engine`

### TDD Task List (write tests first):
1. `test_factory_returns_sequential_mode`
2. `test_factory_returns_random_mode`
3. `test_factory_returns_adaptive_mode`
4. `test_factory_case_insensitive` — `"SEQUENTIAL"` works too
5. `test_factory_raises_for_unknown_mode`
6. `test_sequential_exhausts_deck_in_order`
7. `test_random_mode_returns_all_cards_no_repeats`
8. `test_adaptive_mode_repeats_missed_cards`
9. `test_adaptive_mode_ends_only_when_all_correct`
10. `test_session_stats_accuracy_calculation`
11. `test_answer_is_case_insensitive`
12. `test_answer_strips_leading_trailing_whitespace`
13. `test_session_tracks_missed_cards_correctly`

### `quiz_engine.py` — Strategy Pattern + Factory
```python
from __future__ import annotations
from abc import ABC, abstractmethod

class QuizMode(ABC):
    """Abstract base class for quiz selection strategies."""

    @abstractmethod
    def get_next_card(self) -> FlashCard | None:
        """Return the next card or None if the session is over."""

class SequentialMode(QuizMode): ...
class RandomMode(QuizMode): ...
class AdaptiveMode(QuizMode): ...

class QuizModeFactory:
    """Factory for creating QuizMode instances by name."""

    _MODES: dict[str, type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @staticmethod
    def create(mode: str, deck: list[FlashCard]) -> QuizMode:
        """Create a QuizMode by name (case-insensitive)."""

@dataclass
class SessionStats:
    total: int
    correct: int
    incorrect: int
    missed_cards: list[FlashCard]

    @property
    def accuracy(self) -> float:
        """Computed from correct/total to avoid inconsistency."""
        return (self.correct / self.total * 100) if self.total > 0 else 0.0

class QuizSession:
    """Orchestrates a complete quiz session."""

    def __init__(self, deck: list[FlashCard], mode: QuizMode) -> None: ...
    def next_card(self) -> FlashCard | None: ...
    def answer(self, card: FlashCard, user_input: str) -> bool: ...
    def get_stats(self) -> SessionStats: ...
```

**AdaptiveMode security**: sanitize and cap the retry counter to prevent infinite loops. A card may be retried at most `len(deck) * 3` times total before the session is forced to end.

---

## PHASE 3 — UI LAYER

> Follow the 7-step mandatory workflow. Branch: `feat/phase-3-ui-layer`

### TDD Task List (write tests first):
1. `test_display_card_outputs_front` — verify stdout contains card front
2. `test_display_feedback_correct` — green output for correct answer
3. `test_display_feedback_incorrect` — red output with expected answer
4. `test_display_stats_shows_all_fields` — summary table contains accuracy, total, correct
5. `test_get_user_answer_strips_whitespace` — leading/trailing space removed
6. `test_exit_command_raises_system_exit` — typing `"exit"` → `SystemExit(0)`
7. `test_keyboard_interrupt_raises_system_exit` — `Ctrl+C` → `SystemExit(0)`

### `ui.py`
- Use `colorama` for colored output. **Do NOT call `colorama.init()` in `ui.py`** — it is initialized in `main.py` to avoid global state issues during testing.
- All output functions are pure (testable with `capsys` fixture).
- Answer input is validated: strip whitespace, enforce max 500 chars.

```python
def display_card(card: FlashCard) -> None: ...
def get_user_answer() -> str: ...
def display_feedback(correct: bool, expected: str) -> None: ...
def display_stats(stats: SessionStats) -> None: ...
def display_welcome(deck_size: int, mode: str) -> None: ...
```

Stats table format:
```
════════════════════════════
 📊  SESSION SUMMARY
════════════════════════════
 Total Questions : 10
 Correct         : 8
 Incorrect       : 2
 Accuracy        : 80.0%
════════════════════════════
 ❌ Missed Cards:
  • What is a list? → A mutable sequence
════════════════════════════
```

---

## PHASE 4 — ENTRY POINT

> Follow the 7-step mandatory workflow. Branch: `feat/phase-4-entry-point`

### TDD Task List (write tests first):
1. `test_main_requires_file_argument` — missing `-f` → non-zero exit
2. `test_main_default_mode_is_sequential` — no `-m` → sequential
3. `test_main_invalid_mode_exits_cleanly` — `-m badmode` → `SystemExit` with message
4. `test_main_nonexistent_file_exits_cleanly` — missing file → friendly message
5. `test_main_smoke_sequential` — full run with 3 mocked answers
6. `test_main_smoke_adaptive` — full run in adaptive mode

### `main.py`
```python
from __future__ import annotations
import colorama
colorama.init(autoreset=True)  # Initialize colorama HERE, not in ui.py (avoids global state issues on import)

__version__ = "1.0.0"

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate CLI arguments."""

def run(argv: list[str] | None = None) -> None:
    """Main entry point — orchestrates the full quiz session."""

if __name__ == "__main__":
    run()
```

All exceptions must be caught at the top level. The user must never see a Python traceback. Log the full error to stderr for debugging; show only the friendly message to stdout.

argparse flags:
- `-f` / `--file` (required): path to JSON flashcard file
- `-m` / `--mode` (default: `"sequential"`): quiz mode
- `--stats` (flag): always show stats at the end of a session (stats display is the default behavior, this flag exists for CLI interface compatibility with Udacity requirements)
- `--version` (show `1.0.0` — define version as `__version__ = "1.0.0"` in `main.py` to keep it in one place)

---

## PHASE 5 — TEST SUITE HARDENING

> Follow the 7-step mandatory workflow. Branch: `feat/phase-5-test-hardening`
>
> **Note:** This phase is NOT traditional TDD (code already exists from Phases 1-4). Instead, the workflow is: (1) identify coverage gaps and edge cases, (2) write new tests targeting those gaps, (3) fix any bugs the new tests reveal. The mandatory workflow Step 4 (TDD) should write tests that may expose bugs in existing code — a valid red-green cycle.

At this point, existing tests from Phases 1–4 should already pass. This phase adds edge cases, property-based thinking, and ensures >80% coverage (aim for ≥85%).

### Additional tests to add:
- `test_load_json_with_extra_fields_is_accepted` — extra keys in card dict are ignored
- `test_sequential_with_single_card` — edge: deck of 1
- `test_adaptive_with_all_wrong_then_all_correct` — full retry cycle
- `test_stats_with_zero_questions` — empty session stats
- `test_answer_with_unicode_input` — Unicode answer is handled safely
- `test_file_path_with_spaces` — path with spaces works
- `test_concurrent_sessions_independent` — two sessions don't share state

### `tests/conftest.py` — shared fixtures
```python
from __future__ import annotations
import pytest
from data_loader import FlashCard

@pytest.fixture
def sample_deck() -> list[FlashCard]:
    return [
        FlashCard(front="What is Python?", back="A programming language"),
        FlashCard(front="What is a list?", back="A mutable sequence"),
        FlashCard(front="What is a dict?", back="A key-value mapping"),
    ]

@pytest.fixture
def single_card_deck() -> list[FlashCard]:
    return [FlashCard(front="Q", back="A")]
```

Quality gate for this phase: `pytest --cov=. --cov-report=term-missing` must show **>80%** overall (Udacity minimum). Aim for ≥85%.

---

## PHASE 6 — CONFIGURATION REFINEMENT

> Follow the 7-step mandatory workflow. Branch: `feat/phase-6-config`
>
> **Note:** The base configuration files (`.flake8`, `pyproject.toml`, `pytest.ini`) were already created in Phase 0. This phase reviews and refines them based on lessons learned from Phases 1-5.

### Review and update `.flake8`:
```ini
[flake8]
max-line-length = 99
extend-ignore = E203
exclude = .git,__pycache__,htmlcov,venv,.venv
```
**Note:** `W503` was removed because it is deprecated in flake8 6.x. Flake8 does NOT read `pyproject.toml` — always use the `.flake8` file.

### Review and update `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true
disallow_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

[tool.coverage.run]
omit = ["tests/*"]
```

### Review and update `pytest.ini`:
```ini
[pytest]
testpaths = tests
addopts = --cov=. --cov-report=term-missing
```
**Note:** `--cov-omit` is NOT a valid pytest-cov flag. Coverage omit patterns are configured in `[tool.coverage.run]` in `pyproject.toml`.

---

## PHASE 7 — DOCUMENTATION

> Follow the 7-step mandatory workflow. Branch: `feat/phase-7-documentation`

### `README.md` — professional, complete
Sections required:
1. Project badge line (coverage, python version, license)
2. Description and features
3. Architecture diagram (ASCII) showing modules and their relationships
4. Design patterns used (Strategy + Factory) with a brief explanation of why
5. Prerequisites and installation
6. Usage examples for all 3 modes
7. Running the test suite + interpreting coverage report
8. Security notes (what the app validates and why)
9. Contributing guide (branch naming, PR process)
10. License

### `docs/ai_edit_log.md`
Document **at least 5 genuine AI interaction entries** (Udacity minimum; aim for 7, one per phase). These must reflect real prompts and real AI responses — do not fabricate entries. Format:
```markdown
## Entry N — Phase N: <Phase Name>
**Date:** YYYY-MM-DD
**Prompt used:** "<exact prompt>"
**AI Response Summary:** <2-3 sentences>
**Issue found in AI output:** <specific problem>
**Fix applied:** <what was changed and why>
**Lesson learned:** <1-2 sentences>
```

### `docs/final_report_template.md`
Create the final project report (1000-1500 words) as required by the Udacity rubric. Sections:
1. How AI was used throughout the development process
2. Reflection on what was learned about working with AI tools
3. Examples of AI strengths and weaknesses encountered
4. Decision-making process for accepting/rejecting AI suggestions

### `prompts.md`
Document the prompt evolution across all 7 phases, showing how each prompt was refined based on output quality.

---

## CODE QUALITY STANDARDS (all phases)

| Requirement | Tool | Gate |
|-------------|------|------|
| Style (PEP 8) | flake8 | Zero errors |
| Type safety | mypy | Zero errors (with `disallow_untyped_defs`) |
| Test coverage | pytest-cov | > 80% (Udacity min), aim ≥ 85% |
| No raw tracebacks | manual review | 100% |
| Docstrings | manual review | All public functions |
| Type hints | mypy | All function signatures |
| No bare `except` | flake8 (E722) | Zero violations |
| No magic strings | manual review | Use constants/enums |
| Input validation | tests | All user inputs validated |
| Path safety | tests | Path traversal tests passing |

---

## GIT BRANCHING STRATEGY

```
main (protected)
├── feat/phase-1-data-layer       → PR → merge → delete branch
├── feat/phase-2-quiz-engine      → PR → merge → delete branch
├── feat/phase-3-ui-layer         → PR → merge → delete branch
├── feat/phase-4-entry-point      → PR → merge → delete branch
├── feat/phase-5-test-hardening   → PR → merge → delete branch
├── feat/phase-6-config           → PR → merge → delete branch
└── feat/phase-7-documentation    → PR → merge → delete branch
```

Commit message format (Conventional Commits):
```
<type>(scope): <short description>

Types: feat | fix | test | refactor | docs | chore | security
Examples:
  feat(data-layer): add path traversal validation
  test(quiz-engine): add adaptive mode retry edge cases
  security(file-handler): enforce 10MB file size limit
```

---

## DEFINITION OF DONE

The project is complete when **all** of the following are true:

**Functionality:**
- [ ] `python main.py -f data/python_basics.json -m adaptive` runs a full game
- [ ] `python main.py -f data/python_basics.json -m random` runs without errors
- [ ] `python main.py -f data/python_basics.json` (sequential) works
- [ ] Typing `exit` during a quiz exits cleanly (no traceback)
- [ ] `Ctrl+C` exits cleanly (no traceback)
- [ ] Malformed JSON file shows friendly error and exits

**Quality Gates:**
- [ ] `pytest --cov=. --cov-report=term-missing` → **> 80% coverage (Udacity min), aim ≥ 85%, all passing**
- [ ] `flake8 .` → **zero errors**
- [ ] `python -m mypy . --ignore-missing-imports` → **zero errors**

**Security:**
- [ ] `../../etc/passwd` as file path → rejected with friendly `SystemExit` message
- [ ] 11 MB JSON file → rejected before being read
- [ ] User input > 500 chars → truncated or rejected gracefully

**Git:**
- [ ] 7 merged PRs visible in GitHub
- [ ] 7 plan files in `docs/plans/`
- [ ] All branches deleted after merge
- [ ] All commits follow Conventional Commits format

**Documentation:**
- [ ] `README.md` has all 10 required sections
- [ ] `docs/ai_edit_log.md` has ≥ 5 genuine entries (Udacity minimum; aim for 7)
- [ ] `docs/final_report_template.md` — final report completed (1000-1500 words)
- [ ] `prompts.md` documents all phase prompts

---

## START INSTRUCTIONS

1. Begin with **Phase 0** (repo setup — no plan, no PR needed).
2. After Phase 0, follow the **7-step mandatory workflow** for every subsequent phase.
3. Never start a new phase until the PR for the previous phase is merged.
4. After all 7 PRs are merged, run the full Definition of Done checklist.
5. Report completion with a summary of: total tests, final coverage %, PR links.
