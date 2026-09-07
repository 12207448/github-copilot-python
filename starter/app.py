"""Flask application for the Sudoku game."""

from flask import Flask, jsonify, render_template, request

import sudoku_logic

app = Flask(__name__)

# In-memory store for the active game session
CURRENT = {
    "puzzle": None,
    "solution": None,
    "difficulty": "medium",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new")
def new_game():
    difficulty = request.args.get("difficulty", "medium").lower()
    if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
        return jsonify({"error": f"Invalid difficulty: {difficulty}"}), 400

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    CURRENT["puzzle"] = puzzle
    CURRENT["solution"] = solution
    CURRENT["difficulty"] = difficulty

    return jsonify({
        "puzzle": puzzle,
        "difficulty": difficulty,
        "clues": sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY),
    })


@app.route("/check", methods=["POST"])
def check_solution():
    if CURRENT["solution"] is None:
        return jsonify({"error": "No game in progress. Start a new game first."}), 400

    data = request.get_json(silent=True)
    if not data or "board" not in data:
        return jsonify({"error": "Request must include a board."}), 400

    board = data["board"]
    solution = CURRENT["solution"]
    incorrect = sudoku_logic.find_incorrect_cells(board, solution)
    conflicts = sudoku_logic.find_conflicts(board)
    complete = sudoku_logic.is_board_complete(board, solution)

    return jsonify({
        "incorrect": incorrect,
        "conflicts": conflicts,
        "complete": complete,
    })


@app.route("/hint", methods=["POST"])
def hint():
    if CURRENT["solution"] is None:
        return jsonify({"error": "No game in progress. Start a new game first."}), 400

    data = request.get_json(silent=True)
    if not data or "board" not in data:
        return jsonify({"error": "Request must include a board."}), 400

    board = data["board"]
    hint_cell = sudoku_logic.find_hint_cell(board, CURRENT["solution"])
    if hint_cell is None:
        return jsonify({"error": "No empty cells remaining."}), 400

    return jsonify({"hint": hint_cell})


@app.route("/conflicts", methods=["POST"])
def conflicts():
    """Return live conflict positions for the current board state."""
    data = request.get_json(silent=True)
    if not data or "board" not in data:
        return jsonify({"error": "Request must include a board."}), 400

    return jsonify({"conflicts": sudoku_logic.find_conflicts(data["board"])})


if __name__ == "__main__":
    app.run(debug=True)
