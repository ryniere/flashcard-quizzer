"""
Flask web application for the Flashcard Quizzer.

Provides a browser-based interface for studying flashcards,
reusing the existing data_loader and quiz_engine modules.
"""
from __future__ import annotations

import os
import uuid

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from data_loader import FlashCard, load_flashcards
from quiz_engine import AdaptiveMode, QuizModeFactory, QuizSession

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# In-memory store for active quiz sessions (keyed by session id)
_sessions: dict[str, QuizSession] = {}
_current_cards: dict[str, FlashCard] = {}
_deck_cache: dict[str, list[FlashCard]] = {}


def _list_decks() -> list[dict[str, str]]:
    """Return available deck files from the data directory."""
    decks = []
    if os.path.isdir(DATA_DIR):
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith(".json"):
                name = filename.replace("_", " ").replace(".json", "").title()
                decks.append({"filename": filename, "name": name})
    return decks


def _get_or_create_quiz(
    deck_file: str, mode: str
) -> tuple[QuizSession, str]:
    """Load a deck and create a new quiz session, returning (session, sid)."""
    filepath = os.path.join("data", deck_file)
    cards = load_flashcards(filepath)
    quiz_mode = QuizModeFactory.create(mode, cards)
    quiz_session = QuizSession(deck=cards, mode=quiz_mode)
    sid = uuid.uuid4().hex
    _sessions[sid] = quiz_session
    _deck_cache[sid] = cards
    return quiz_session, sid


@app.route("/")
def index() -> str:
    """Home page — choose a deck and quiz mode."""
    decks = _list_decks()
    return render_template("index.html", decks=decks)


@app.route("/start", methods=["POST"])
def start_quiz() -> str:
    """Start a new quiz session."""
    deck_file = request.form.get("deck", "")
    mode = request.form.get("mode", "sequential")

    if not deck_file:
        return redirect(url_for("index"))

    try:
        quiz_session, sid = _get_or_create_quiz(deck_file, mode)
    except (SystemExit, ValueError) as exc:
        decks = _list_decks()
        return render_template("index.html", decks=decks, error=str(exc))

    session["quiz_sid"] = sid
    session["mode"] = mode
    session["deck_file"] = deck_file

    card = quiz_session.next_card()
    if card is None:
        return redirect(url_for("index"))

    _current_cards[sid] = card
    stats = quiz_session.get_stats()
    total_cards = len(_deck_cache[sid])
    return render_template(
        "quiz.html",
        card=card,
        stats=stats,
        mode=mode,
        deck_name=deck_file.replace("_", " ").replace(".json", "").title(),
        card_number=stats.total + 1,
        total_cards=total_cards,
    )


@app.route("/answer", methods=["POST"])
def answer() -> str:
    """Process an answer and show feedback, then the next card."""
    sid = session.get("quiz_sid", "")
    quiz_session = _sessions.get(sid)  # type: ignore[arg-type]

    if quiz_session is None:
        return redirect(url_for("index"))

    user_answer = request.form.get("answer", "")
    card = _current_cards.get(sid)

    if card is None:
        return redirect(url_for("results"))

    is_correct = quiz_session.answer(card, user_answer)
    expected = card.back

    # Get next card
    next_card = quiz_session.next_card()
    stats = quiz_session.get_stats()
    total_cards = len(_deck_cache[sid])
    mode = session.get("mode", "sequential")
    deck_name = session.get("deck_file", "").replace("_", " ").replace(".json", "").title()

    if next_card is None:
        # Quiz is over — store stats for results page
        session["final_stats"] = {
            "total": stats.total,
            "correct": stats.correct,
            "incorrect": stats.incorrect,
            "accuracy": round(stats.accuracy, 1),
            "missed": [
                {"front": c.front, "back": c.back} for c in stats.missed_cards
            ],
        }
        force_stopped = (
            isinstance(quiz_session._mode, AdaptiveMode)
            and quiz_session._mode.was_force_stopped
        )
        session["force_stopped"] = force_stopped
        # Clean up
        _sessions.pop(sid, None)
        _current_cards.pop(sid, None)
        _deck_cache.pop(sid, None)

        return render_template(
            "feedback.html",
            is_correct=is_correct,
            user_answer=user_answer,
            expected=expected,
            card=card,
            quiz_over=True,
            stats=stats,
            mode=mode,
            deck_name=deck_name,
            card_number=stats.total,
            total_cards=total_cards,
        )

    _current_cards[sid] = next_card
    return render_template(
        "feedback.html",
        is_correct=is_correct,
        user_answer=user_answer,
        expected=expected,
        card=card,
        quiz_over=False,
        stats=stats,
        mode=mode,
        deck_name=deck_name,
        card_number=stats.total + 1,
        total_cards=total_cards,
        next_card=next_card,
    )


@app.route("/next", methods=["POST"])
def next_card() -> str:
    """Show the next card in the quiz."""
    sid = session.get("quiz_sid", "")
    quiz_session = _sessions.get(sid)  # type: ignore[arg-type]

    if quiz_session is None:
        return redirect(url_for("index"))

    card = _current_cards.get(sid)
    if card is None:
        return redirect(url_for("results"))

    stats = quiz_session.get_stats()
    total_cards = len(_deck_cache[sid])
    mode = session.get("mode", "sequential")
    deck_name = session.get("deck_file", "").replace("_", " ").replace(".json", "").title()

    return render_template(
        "quiz.html",
        card=card,
        stats=stats,
        mode=mode,
        deck_name=deck_name,
        card_number=stats.total + 1,
        total_cards=total_cards,
    )


@app.route("/results")
def results() -> str:
    """Display quiz results."""
    final_stats = session.get("final_stats")
    if final_stats is None:
        return redirect(url_for("index"))

    force_stopped = session.get("force_stopped", False)
    mode = session.get("mode", "sequential")
    deck_name = session.get("deck_file", "").replace("_", " ").replace(".json", "").title()
    return render_template(
        "results.html",
        stats=final_stats,
        force_stopped=force_stopped,
        mode=mode,
        deck_name=deck_name,
    )


@app.route("/api/decks")
def api_decks() -> tuple:
    """JSON endpoint returning available decks."""
    return jsonify(_list_decks()), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
