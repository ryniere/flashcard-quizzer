# Flashcard Quizzer

![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Description and Features

Flashcard Quizzer is a terminal-based study tool that loads flashcard decks from
JSON files and quizzes you directly in the command line. It tracks your accuracy
in real time, highlights missed cards at the end of each session, and supports
three distinct quiz modes so you can study the way that works best for you.

**Core features:**

- **Sequential mode** -- presents cards in deck order for structured review.
- **Random mode** -- shuffles the deck so you never rely on positional memory.
- **Adaptive mode** -- re-queues cards you answer incorrectly until you get them
  right (with a retry cap of 3x the deck size to prevent infinite loops).
- Colored terminal output with session summary statistics.
- Secure file I/O with path traversal prevention and file size limits.
- Flexible JSON input: accepts both flat arrays and `{"cards": [...]}` objects.

## Architecture

```
                         +------------+
                         |  main.py   |
                         +-----+------+
                               |
              +----------------+----------------+
              |                |                |
     +--------v-----+  +------v-------+  +-----v----+
     | data_loader.py|  | quiz_engine.py|  |  ui.py   |
     | (FlashCard)   |  | (QuizSession) |  | (display)|
     +--------+------+  +------+-------+  +----------+
              |                |
              |         +------+------+
              |         |  Strategy   |
              |         |  Pattern    |
              |         +------+------+
              |                |
              |    +-----------+-----------+
              |    |           |           |
              | +--v---+  +---v--+  +-----v----+
              | |Sequ- |  |Rand- |  | Adaptive |
              | |ential|  | om   |  |   Mode   |
              | +------+  +------+  +----------+
              |
     +--------v---------+      +-------------------+
     | utils/            |      |   Factory Pattern  |
     |  file_handler.py  |      | QuizModeFactory    |
     | (secure file I/O) |      | .create(name,deck) |
     +-------------------+      +-------------------+

 QuizMode (ABC)  <--- SequentialMode
                 <--- RandomMode
                 <--- AdaptiveMode
```

**Module responsibilities:**

| Module | Purpose |
|--------|---------|
| `main.py` | CLI argument parsing, orchestration, error handling |
| `data_loader.py` | JSON loading, validation, `FlashCard` dataclass |
| `quiz_engine.py` | `QuizSession`, `QuizMode` ABC, three mode strategies, `QuizModeFactory` |
| `ui.py` | Colored terminal output, input handling, stats display |
| `utils/file_handler.py` | Path validation, file size checks, secure reads |

## Design Patterns

### Strategy Pattern

The `QuizMode` abstract base class defines a single method -- `get_next_card()`.
Each concrete strategy (`SequentialMode`, `RandomMode`, `AdaptiveMode`)
implements its own card-selection algorithm. `QuizSession` delegates card
retrieval to whichever strategy was injected at construction time, so the session
logic never changes when a new mode is added.

**Why:** Keeps quiz orchestration decoupled from card-ordering logic. Adding a
fourth mode (e.g., spaced-repetition) requires only a new class and a one-line
factory registration -- zero changes to `QuizSession` or `main.py`.

### Factory Pattern

`QuizModeFactory.create(mode_name, deck)` maps a string name to the correct
`QuizMode` subclass. The CLI passes the user's `--mode` flag directly to the
factory, which handles validation and instantiation.

**Why:** Centralizes object creation in one place, eliminates scattered
`if/elif` chains, and makes mode registration explicit and auditable.

## Prerequisites and Installation

**Prerequisites:**

- Python 3.9 or higher
- pip (included with Python 3.9+)
- Git (for cloning the repository)

**Installation:**

```bash
git clone <repository-url>
cd Frashcard-Quizzer

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Usage Examples

Flashcard files live in the `data/` directory. Two sample decks are included:
`python_basics.json` and `science_facts.json`.

### Sequential Mode (default)

Cards are presented in the order they appear in the file.

```bash
python main.py -f data/python_basics.json
```

### Random Mode

Cards are shuffled before the session begins. Every card appears exactly once.

```bash
python main.py -f data/python_basics.json -m random
```

### Adaptive Mode

Missed cards are re-queued until you answer them correctly (capped at 3x total
serves to prevent infinite loops).

```bash
python main.py -f data/python_basics.json -m adaptive
```

### Additional Flags

```bash
# Display version
python main.py --version

# Display help
python main.py --help
```

### Flashcard File Format

You can use either format:

```json
[
  {"front": "What is Python?", "back": "A programming language."}
]
```

```json
{
  "cards": [
    {"front": "What is Python?", "back": "A programming language."}
  ]
}
```

## Running the Test Suite

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Generate an HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser to inspect per-file coverage.
```

### Interpreting the Coverage Report

The `term-missing` flag prints a table showing each source file, the percentage
of lines covered, and the specific line numbers that lack coverage. A healthy
target is 90%+ overall. The current suite achieves **99% coverage**.

```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
data_loader.py             30      0   100%
quiz_engine.py             55      0   100%
ui.py                      25      1    96%   ...
utils/file_handler.py      22      0   100%
-----------------------------------------------------
TOTAL                     132      1    99%
```

If coverage drops after a change, check the `Missing` column to find untested
lines and add corresponding test cases before merging.

## Security Notes

The application enforces several defensive measures in `utils/file_handler.py`:

- **Path traversal prevention** -- All file paths are resolved to absolute paths
  with `os.path.realpath()` (resolving symlinks) and validated against a
  `SAFE_BASE_DIR` anchored to the project root. Paths containing `../` or
  symlinks that escape the project directory are rejected with a `ValueError`.
- **File size limits** -- Files larger than 10 MB are rejected before reading to
  prevent memory exhaustion.
- **Input length limits** -- User input in the terminal is truncated to 500
  characters (`MAX_INPUT_LENGTH` in `ui.py`) to prevent abuse.
- **JSON validation** -- Every card is validated for required fields (`front`,
  `back`) and correct types before use. Malformed data produces clear error
  messages and a clean exit.

## Contributing

Contributions are welcome. Please follow the guidelines below to keep the
project consistent and reviewable.

### Branch Naming

Use the prefix pattern tied to the project phase:

```
feat/phase-1-add-random-mode
feat/phase-2-adaptive-retry-cap
fix/phase-3-path-traversal-edge-case
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification:

```
feat: add adaptive quiz mode with retry cap
fix: reject symlinks that escape SAFE_BASE_DIR
test: cover edge cases for empty deck validation
docs: update README architecture diagram
```

### Pull Request Process

1. Create a feature branch from `main` using the naming convention above.
2. Write or update tests so coverage does not decrease.
3. Run the full quality check before pushing:
   ```bash
   black . && isort . && flake8 . && mypy . && pytest --cov=.
   ```
4. Open a pull request with a clear description of what changed and why.
5. Address all review feedback before requesting a re-review.

## License

This project is licensed under the MIT License. See [LICENSE.txt](LICENSE.txt)
for details.
