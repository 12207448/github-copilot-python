# GitHub Copilot Instructions: Sudoku Flask Project

Use this document as the primary project context when proposing or implementing
changes in this directory.

## Project overview

This is a Flask-backed Sudoku web game. The backend generates puzzles and owns
the solution, while the browser provides the interactive game UI using plain
JavaScript. Do not introduce a frontend framework.

## Architecture

```text
starter/
├── app.py                  # Flask application and JSON API routes
├── sudoku_logic.py         # Sudoku generation, solving, and validation
├── requirements.txt        # Python runtime and test dependencies
├── pytest.ini              # Pytest configuration
├── templates/
│   └── index.html          # Page structure and accessible controls
├── static/
│   ├── main.js             # Browser game state and API integration
│   └── styles.css          # Layout, responsive styles, and themes
└── tests/
    ├── conftest.py         # Test import configuration
    └── test_sudoku_logic.py
```

### Backend responsibilities

- Keep Sudoku algorithms in `sudoku_logic.py`.
- Keep HTTP routing and request/response handling in `app.py`.
- Store the active puzzle and solution in the existing in-memory `CURRENT`
  state unless persistence is explicitly requested.
- Expose JSON responses for game actions:
  - `GET /new?difficulty=easy|medium|hard`
  - `POST /check`
  - `POST /hint`
  - `POST /conflicts`
- Validate request data and return a clear JSON error with an appropriate
  status code instead of silently accepting invalid input.

### Frontend responsibilities

- Keep the frontend framework-free: use standard browser JavaScript only.
- Use the existing Flask API for puzzle generation, checking, and hints.
- Keep browser-only state such as the timer, hints used, theme preference, and
  leaderboard in `static/main.js`.
- Keep markup in `templates/index.html` and visual behavior in
  `static/styles.css`.

## Code style standards

### Python

- Follow PEP 8 and use descriptive `snake_case` names.
- Add type hints and concise docstrings to public functions.
- Prefer small, deterministic helpers over duplicated logic.
- Use `deep_copy` or another isolated copy when a backtracking operation
  mutates a board.
- Do not use broad exception handlers or silently fall back after an error.
- Keep constants such as `SIZE`, `EMPTY`, and `DIFFICULTY_CLUES` centralized in
  `sudoku_logic.py`.

### JavaScript

- Use `const` and `let`; never add `var`.
- Use descriptive function names and small functions organized by concern.
- Use `fetch` for API calls and handle both network failures and non-2xx
  responses.
- Escape user-provided leaderboard names before rendering them as HTML.
- Prefer DOM APIs and `textContent` over unsafe HTML interpolation.
- Prefer event delegation on `#sudoku-board` for cell input and focus handling.
- Keep live conflict detection client-side so it responds immediately without
  a server round-trip.

### HTML and CSS

- Preserve semantic elements, labels, button names, and accessible attributes.
- Use CSS classes rather than inline styles.
- Define shared colors with custom properties in `:root`, with dark-mode
  overrides under `[data-theme="dark"]`.
- Keep Sudoku cell dimensions stable when adding borders; avoid layout shifts.
- Preserve the `block-a` and `block-b` classes for the alternating 3x3
  checkerboard pattern.
- Keep the layout responsive for narrow screens.

## Functional requirements

1. Every generated puzzle must have exactly one solution.
2. Use backtracking with `count_solutions(board, limit=2)` to verify
   uniqueness. Stop counting after two solutions.
3. Removing a cell from a complete solution must restore it when the removal
   produces zero or multiple solutions.
4. Difficulty levels must remain:
   - Easy: 40 clues
   - Medium: 35 clues
   - Hard: 28 clues
5. `/new` must validate the difficulty and pass the selected level through to
   puzzle generation.
6. Prefilled puzzle cells must be locked and visually distinct from editable
   cells.
7. A player-entered duplicate must immediately highlight every conflicting
   cell in its row, column, or 3x3 box with a red border.
8. The Hint button must call `POST /hint`, fill one correct random empty cell,
   lock that cell, apply green hint styling, and increment the hint count.
9. The timer must start with a new game and stop when the puzzle is complete.
10. Completion must allow the player to save a leaderboard entry containing
    name, time in seconds, difficulty, and hints used.
11. The leaderboard must be sorted by fastest time, limited to 10 entries, and
    persisted in `localStorage` under `sudoku_top10`.
12. The dark/light preference must be persisted under `sudoku_theme`.
13. The theme toggle must use a sun/moon icon button in the top-right corner.

## Testing approach

- Use pytest for backend logic tests.
- Run tests from this directory:

  ```bash
  pytest tests/ -v
  ```

- Tests should cover:
  - empty board creation;
  - safe cell placement;
  - complete valid board generation;
  - unique solution validation;
  - clue counts for all difficulty levels;
  - row, column, and box conflict detection;
  - hint cell selection;
  - invalid difficulty handling.
- When changing backend behavior, add or update a focused test before relying
  on manual verification.
- Run `git diff --check` after edits.

## Things to avoid

- Do not add React, Redux, Vue, jQuery, or another frontend framework.
- Do not move puzzle generation, solution ownership, or authoritative solution
  checking into the browser.
- Do not remove or rename `/new`, `/check`, `/hint`, or `/conflicts` without
  updating all callers and tests.
- Do not weaken the unique-solution guarantee to reach a target clue count.
- Do not trust client-submitted completion or score data as authoritative
  server state.
- Do not use blocking prompts where the existing modal can be used.
- Do not add inline styles, duplicate theme values, or hard-coded colors that
  bypass the CSS custom-property system.
- Do not swallow exceptions with broad `try/except` or generic silent
  fallbacks.
- Do not reset or overwrite unrelated user changes in the working tree.

## Change checklist

Before finishing a change:

1. Inspect the existing implementation and reuse established helpers.
2. Make the smallest complete change across all affected layers.
3. Update tests when backend behavior changes.
4. Run the targeted pytest command and check for formatting errors.
5. Confirm that existing API routes, localStorage keys, accessibility labels,
   and responsive behavior remain compatible.
