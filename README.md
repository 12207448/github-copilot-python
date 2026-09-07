# Refactor a Sudoku Game written in Python Flask

Use this Sudoku game to practice your skills with GitHub Copilot. The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

### Dependencies

- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3

### Installation

1. Fork this repository to your GitHub account.

2. Clone your forked repository to your local machine.

3. Open a terminal and navigate to the `starter` directory:

```bash
cd starter
```

4. Create a Python virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

5. Install required Python packages:

```bash
pip install -r requirements.txt
```

6. Run the Flask app:

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Running Tests

Tests use **pytest**. Run them from the `starter` directory:

```bash
pytest tests/ -v
```

For a quick summary:

```bash
pytest tests/ -q
```

## Features

- **Difficulty selector** — Easy, Medium, and Hard puzzles with different clue counts
- **Unique solution validation** — every generated puzzle has exactly one solution
- **Live input feedback** — conflicting entries are highlighted immediately via event delegation on the board
- **Check button** — highlights incorrect and conflicting cells
- **Hint button** — fills one correct cell (styled green) and locks it
- **Timer** — tracks solve time from new game start
- **Top 10 leaderboard** — saved in browser localStorage (name, time, difficulty, hints)
- **Dark/light mode** — toggle with persistent theme preference
- **Responsive layout** — works on desktop and mobile
- **Alternating 3×3 block colors** — checkerboard pattern for visual clarity

## Project Structure

```
starter/
├── app.py                  # Flask routes
├── sudoku_logic.py         # Puzzle generation & validation
├── instruction.md          # Copilot guidance file
├── templates/index.html    # Game page
├── static/
│   ├── main.js             # Client-side game logic
│   └── styles.css          # Theming and layout
├── tests/
│   ├── conftest.py
│   ├── test_sudoku_logic.py
│   └── test_app.py         # Flask API route tests
└── Screenshots/            # Copilot conversation screenshots
```

## Copilot Instructions

See `starter/instruction.md` for the instruction file that guides Copilot on code style, architecture, and project requirements.

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation on the Sudoku board.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.
