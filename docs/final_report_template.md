# AI-Assisted Development Project Report

**Student Name:** Ryniere Silva
**Project Title:** Flashcard Quizzer CLI
**Date:** 2026-03-18

---

## 1. Introduction

The Flashcard Quizzer is a command-line application that lets users study
flashcard decks from JSON files using three quiz modes: sequential, random, and
adaptive. I built it as the capstone project for the Udacity AI-Assisted
Development course, where the primary goal was not just to ship working software
but to learn how to collaborate effectively with an AI coding assistant while
maintaining professional engineering standards.

The application is implemented in Python and consists of four core modules: a
data loader with security-hardened file handling, a quiz engine built around the
Strategy and Factory design patterns, a terminal UI with colored output, and a
CLI entry point that wires everything together. The project follows a strict
seven-phase workflow, where each phase uses test-driven development, subagent
delegation, pull request review, and iterative prompt refinement. The final
codebase contains 64 tests with 99% line coverage and passes flake8, mypy, and
all quality gates with zero errors.

## 2. AI Collaboration Process

I used Claude Code as my sole AI assistant. Every phase followed the same
sequence:

**Planning.** Each phase began with a plan (`docs/plans/phase-N-plan.md`)
specifying the objective, files to change, a TDD task list with exact test
names, security considerations, and acceptance criteria. Writing the plan
first forced me to think through the design and gave the AI the context it
needed to produce focused output.

**TDD with subagents.** I created a feature branch, wrote all tests against
stub modules (the "red" phase), then dispatched Claude Code subagents to
implement each module in parallel. Each subagent read the plan and the failing
tests before writing code, then ran pytest to confirm all tests passed (the
"green" phase).

**PR review as feedback loop.** After implementation, I opened a pull request.
The review step consistently surfaced issues that neither I nor the AI had
anticipated. Findings were addressed before merging, and the lessons were
folded into the next phase's prompt.

**Iterative prompt refinement.** Phase 1 taught me that security prompts need
exact mechanisms (e.g., `os.path.commonpath`). Phase 3 taught me to enumerate
every exit signal. Phase 5 taught me to reference specific uncovered lines.
By Phase 7, my prompts were far more precise than where I started.

## 3. Design Decisions

The quiz engine uses the **Strategy Pattern** to encapsulate card selection
logic. The abstract base class `QuizMode` defines a single method,
`get_next_card()`, which returns the next card or `None` when the session is
over. Three concrete strategies implement this interface:

- `SequentialMode` iterates through the deck in order.
- `RandomMode` shuffles the deck and iterates through the shuffled copy.
- `AdaptiveMode` uses a deque to re-enqueue incorrectly answered cards until
  all are answered correctly or a retry cap is reached.

The Strategy Pattern was the right choice here because the three modes share the
same interface but differ entirely in their internal logic. Adding a new mode
(for example, a spaced-repetition mode) requires only a new class that
implements `get_next_card()` -- no changes to the session orchestrator.

The **Factory Pattern** complements the Strategy Pattern by mapping a
user-provided mode string to the correct strategy class. `QuizModeFactory`
holds a dictionary of registered modes and performs case-insensitive lookup.
This keeps the CLI entry point clean: `main.py` calls
`QuizModeFactory.create(args.mode, deck)` and receives a ready-to-use mode
object without knowing which concrete class was instantiated.

Both patterns together achieve a key design goal: the quiz session
(`QuizSession`) depends only on the `QuizMode` abstraction, not on any concrete
mode. This makes the session fully testable -- tests can inject any mode
implementation, including mocks.

## 4. AI Strengths Observed

**Fast scaffolding.** Given the TDD task list and module signatures, Claude
Code produced complete test files and implementations in seconds. Dataclass
definitions, argparse configuration, and pytest fixtures were correct on the
first attempt virtually every time.

**TDD compliance.** Because each subagent read the failing tests before
writing code, the AI never drifted from the specification. This produced
tightly aligned implementations.

**Parallel implementation.** Dispatching separate subagents for independent
modules reduced side effects and produced cleaner module boundaries.

**Pattern application.** When given specific class names and method signatures,
the AI produced textbook-quality Strategy and Factory implementations.

## 5. AI Weaknesses Encountered

**Security bypass via `startswith`.** In Phase 1, the AI's first
implementation of `_validate_path()` used `str.startswith()` to check whether
the resolved path was inside the project directory. This is a classic security
bug: if `SAFE_BASE_DIR` is `/home/project`, then `/home/project-evil/secret`
passes the `startswith` check. The PR review caught this, and I refined the
prompt to require `os.path.commonpath()` instead. The AI did not self-detect
this vulnerability.

**Value vs. identity equality.** In Phase 2, the AI tracked missed cards
using `==` (value equality). This meant that two cards with identical
`front`/`back` text were treated as the same card, causing the missed-cards
list to under-count. The fix was to track cards by `id()` (object identity).
The AI defaulted to the more common comparison operator without considering
whether the use case required identity semantics.

**Missing edge cases.** In Phase 3, the AI handled `KeyboardInterrupt` in
`get_user_answer()` but did not handle `EOFError`. When stdin is piped
(which happens in CI and automated testing), reaching end-of-file raises
`EOFError`, not `KeyboardInterrupt`. This caused the application to crash with
a raw traceback in exactly the environment where it most needed to be robust.
The AI only implemented the exit paths that were explicitly listed in the
prompt.

## 6. Decision-Making Process

My process for evaluating AI suggestions followed a consistent pattern:

**PR reviews caught structural issues.** The most impactful feedback came from
the PR review step, which evaluated the code against security requirements,
edge cases, and design consistency. Every PR produced actionable findings:
Phase 1's review caught the `startswith` security bypass, Phase 2's review
caught the identity-vs-equality bug, Phase 3's review caught the missing
`EOFError` handler, and Phase 4's review caught the missing stats display on
early exit.

**Regression tests validated fixes.** For every bug found in a PR review, I
wrote a regression test before applying the fix. This ensured the fix was
correct and prevented the same bug from reappearing in later phases. Examples
include `test_validate_path_rejects_sibling_directory`,
`test_missed_cards_tracks_duplicates_by_identity`,
`test_eof_raises_system_exit`, and `test_adaptive_force_stop_warning`.

**The plan file was the source of truth.** When the AI's output deviated from
the plan, I treated the plan as authoritative and refined the prompt rather
than accepting the deviation. This kept the architecture consistent across
phases and prevented scope creep.

## 7. Testing Strategy

I followed strict TDD: red-green-refactor for every phase. Stub modules raised
`NotImplementedError` so pytest could collect and fail tests (red). Subagents
implemented code to pass those tests (green). I then reviewed for clarity and
style (refactor).

The final suite contains **64 tests** across five files:
`test_flashcard_loader.py` (18 tests: loading, errors, path traversal, size
limits), `test_quiz_modes.py` (18 tests: factory, modes, stats, answer
matching), `test_ui.py` (8 tests: display, input, exits),
`test_integration.py` (10 tests: CLI parsing, smoke tests, error containment),
and `test_edge_cases.py` (10 tests: Unicode, spaces, concurrency, coverage
gaps). Coverage stands at **99%**, well above the 80% minimum.

## 8. Conclusion

This project fundamentally changed how I think about working with AI coding
assistants. Three lessons stand out:

**Precision in prompts is non-negotiable.** The AI produces what you ask for,
not what you mean. A prompt that says "validate the file path" gets a
superficially correct implementation that fails adversarial inputs. A prompt
that says "resolve symlinks with `os.path.realpath()`, then verify containment
with `os.path.commonpath()`" gets a hardened implementation on the first try.
Every refinement I made across the seven phases was a move from vague intent to
precise specification.

**PR review is the essential feedback loop.** Without the review step, I would
have shipped code with a path traversal bypass, an identity-vs-equality bug,
and a missing EOF handler. The AI does not self-audit for these issues. The
human review step is what transforms "code that compiles" into "code that is
correct."

**TDD and AI are a strong combination.** Writing tests first and then
dispatching subagents to implement against those tests produced a tight
feedback loop. The tests served as an executable specification that the AI
could not misinterpret. Every bug found in a PR review was immediately captured
as a regression test, which prevented the same class of bug from reappearing.
The result was a codebase with 64 tests, 99% coverage, and zero quality-gate
failures -- a level of rigor that would have taken significantly longer without
AI assistance but would not have been trustworthy without the human review that
guided it.
