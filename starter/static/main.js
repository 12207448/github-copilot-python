/**
 * Sudoku game client — board rendering, timer, hints, leaderboard, and live feedback.
 *
 * Copilot suggested React/Redux for state management — rejected.
 * This project uses vanilla JavaScript with Flask; game state stays in this file.
 */
const SIZE = 9;
const LEADERBOARD_KEY = "sudoku_top10";
const THEME_KEY = "sudoku_theme";

let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let gameActive = false;
let currentDifficulty = "medium";

// ── Theme ──────────────────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || "light";
  document.documentElement.setAttribute("data-theme", saved === "dark" ? "dark" : "light");
  updateThemeIcon();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem(THEME_KEY, next);
  updateThemeIcon();
}

function updateThemeIcon() {
  const icon = document.querySelector(".theme-icon");
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  icon.textContent = isDark ? "\u263E" : "\u2600";
}

// ── Timer ──────────────────────────────────────────────────────────────────

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  gameActive = true;
  timerInterval = setInterval(() => {
    if (gameActive) {
      elapsedSeconds++;
      updateTimerDisplay();
    }
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function updateTimerDisplay() {
  document.getElementById("timer").textContent = `Time: ${formatTime(elapsedSeconds)}`;
}

// ── Board rendering ────────────────────────────────────────────────────────

function getBlockClass(row, col) {
  const blockRow = Math.floor(row / 3);
  const blockCol = Math.floor(col / 3);
  return (blockRow + blockCol) % 2 === 0 ? "block-a" : "block-b";
}

function createBoardElement() {
  const boardDiv = document.getElementById("sudoku-board");
  boardDiv.innerHTML = "";

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement("input");
      input.type = "text";
      input.inputMode = "numeric";
      input.maxLength = 1;
      input.className = `sudoku-cell ${getBlockClass(i, j)}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute("role", "gridcell");
      input.setAttribute("aria-label", `Row ${i + 1}, Column ${j + 1}`);
      boardDiv.appendChild(input);
    }
  }
}

function getInputs() {
  return document.getElementById("sudoku-board").querySelectorAll(".sudoku-cell");
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const inputs = getInputs();

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];

      inp.className = `sudoku-cell ${getBlockClass(i, j)}`;

      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add("prefilled");
      } else {
        inp.value = "";
        inp.disabled = false;
      }
    }
  }
}

function readBoard() {
  const inputs = getInputs();
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

// ── Live feedback ──────────────────────────────────────────────────────────

function findLocalConflicts(board) {
  const conflicts = new Set();

  function markDuplicates(cells) {
    const seen = {};
    for (const [row, col, val] of cells) {
      if (!seen[val]) {
        seen[val] = [];
      }
      seen[val].push([row, col]);
    }
    for (const positions of Object.values(seen)) {
      if (positions.length > 1) {
        for (const [r, c] of positions) {
          conflicts.add(r * SIZE + c);
        }
      }
    }
  }

  for (let row = 0; row < SIZE; row++) {
    const cells = [];
    for (let col = 0; col < SIZE; col++) {
      if (board[row][col] !== 0) cells.push([row, col, board[row][col]]);
    }
    markDuplicates(cells);
  }

  for (let col = 0; col < SIZE; col++) {
    const cells = [];
    for (let row = 0; row < SIZE; row++) {
      if (board[row][col] !== 0) cells.push([row, col, board[row][col]]);
    }
    markDuplicates(cells);
  }

  for (let br = 0; br < 3; br++) {
    for (let bc = 0; bc < 3; bc++) {
      const cells = [];
      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          const row = br * 3 + i;
          const col = bc * 3 + j;
          if (board[row][col] !== 0) cells.push([row, col, board[row][col]]);
        }
      }
      markDuplicates(cells);
    }
  }

  return conflicts;
}

function applyConflictHighlights(conflicts) {
  const inputs = getInputs();
  inputs.forEach((inp, idx) => {
    inp.classList.remove("conflict", "incorrect");
    if (conflicts.has(idx)) {
      inp.classList.add("conflict");
    }
  });
}

function onCellInput(e) {
  const inp = e.target;
  const val = inp.value.replace(/[^1-9]/g, "");
  inp.value = val;

  inp.classList.remove("incorrect", "hint-cell");

  const board = readBoard();
  const conflicts = findLocalConflicts(board);
  applyConflictHighlights(conflicts);

  clearMessage();
  maybeCompleteAfterInput(board, conflicts);
}

function onCellFocus(e) {
  e.target.select();
}

function clearHighlights() {
  const inputs = getInputs();
  inputs.forEach((inp) => {
    inp.classList.remove("incorrect", "conflict");
  });
}

function initBoardEventDelegation() {
  const boardDiv = document.getElementById("sudoku-board");
  boardDiv.addEventListener("input", (e) => {
    if (e.target.classList.contains("sudoku-cell")) {
      onCellInput(e);
    }
  });
  boardDiv.addEventListener("focusin", (e) => {
    if (e.target.classList.contains("sudoku-cell")) {
      onCellFocus(e);
    }
  });
}

function applyCheckResult(data) {
  const inputs = getInputs();
  const incorrectSet = new Set(data.incorrect.map(([r, c]) => r * SIZE + c));
  const conflictSet = new Set(data.conflicts.map(([r, c]) => r * SIZE + c));

  inputs.forEach((inp, idx) => {
    if (inp.disabled || inp.classList.contains("hint-cell")) return;
    if (incorrectSet.has(idx)) {
      inp.classList.add("incorrect");
    }
    if (conflictSet.has(idx)) {
      inp.classList.add("conflict");
    }
  });

  if (data.complete) {
    gameActive = false;
    stopTimer();
    showCompletionModal();
    return true;
  }

  return false;
}

async function maybeCompleteAfterInput(board, conflicts) {
  if (!gameActive || conflicts.size > 0) {
    return;
  }

  const isFull = board.every((row) => row.every((cell) => cell !== 0));
  if (!isFull) {
    return;
  }

  try {
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board }),
    });
    const data = await res.json();
    if (res.ok && data.complete) {
      applyCheckResult(data);
    }
  } catch {
    // Ignore network errors during background completion checks.
  }
}

// ── Game actions ───────────────────────────────────────────────────────────

async function newGame() {
  const difficulty = document.getElementById("difficulty").value;
  currentDifficulty = difficulty;
  hintsUsed = 0;
  gameActive = false;
  stopTimer();
  clearMessage();
  hideModal();

  try {
    const res = await fetch(`/new?difficulty=${difficulty}`);
    const data = await res.json();
    if (!res.ok) {
      showMessage(data.error || "Failed to start new game.", "error");
      return;
    }
    renderPuzzle(data.puzzle);
    startTimer();
  } catch {
    showMessage("Could not connect to the server.", "error");
  }
}

async function checkSolution() {
  const board = readBoard();
  clearHighlights();

  try {
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board }),
    });
    const data = await res.json();

    if (!res.ok) {
      showMessage(data.error || "Check failed.", "error");
      return;
    }

    const completed = applyCheckResult(data);
    const incorrectCount = data.incorrect.length;
    const conflictCount = data.conflicts.length;

    if (!completed && incorrectCount === 0 && conflictCount === 0) {
      showMessage("Looking good so far! Keep going.", "success");
    } else if (!completed) {
      showMessage("Some cells are incorrect.", "error");
    }
  } catch {
    showMessage("Could not connect to the server.", "error");
  }
}

async function requestHint() {
  const board = readBoard();

  try {
    const res = await fetch("/hint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board }),
    });
    const data = await res.json();

    if (!res.ok) {
      showMessage(data.error || "No hints available.", "error");
      return;
    }

    const [row, col, value] = data.hint;
    const idx = row * SIZE + col;
    const inputs = getInputs();
    const inp = inputs[idx];

    inp.value = value;
    inp.disabled = true;
    inp.classList.remove("conflict", "incorrect");
    inp.classList.add("hint-cell");
    hintsUsed++;

    const updatedBoard = readBoard();
    applyConflictHighlights(findLocalConflicts(updatedBoard));

    if (await isComplete(updatedBoard)) {
      gameActive = false;
      stopTimer();
      showCompletionModal();
    }
  } catch {
    showMessage("Could not connect to the server.", "error");
  }
}

async function isComplete(board) {
  const res = await fetch("/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ board }),
  });
  const data = await res.json();
  return data.complete === true;
}

// ── Messages & modal ─────────────────────────────────────────────────────

function showMessage(text, type) {
  const msg = document.getElementById("message");
  msg.textContent = text;
  msg.className = `message ${type || ""}`;
}

function clearMessage() {
  const msg = document.getElementById("message");
  msg.textContent = "";
  msg.className = "message";
}

function showCompletionModal() {
  const modal = document.getElementById("completion-modal");
  const modalMsg = document.getElementById("modal-message");
  modalMsg.textContent =
    `You solved the puzzle in ${formatTime(elapsedSeconds)} ` +
    `with ${hintsUsed} hint${hintsUsed !== 1 ? "s" : ""} on ${currentDifficulty} difficulty!`;
  document.getElementById("player-name").value = "";
  modal.classList.remove("hidden");
  document.getElementById("player-name").focus();
}

function hideModal() {
  document.getElementById("completion-modal").classList.add("hidden");
}

function saveScore() {
  const name = document.getElementById("player-name").value.trim() || "Anonymous";
  const scores = getLeaderboard();

  scores.push({
    name,
    time: elapsedSeconds,
    level: currentDifficulty,
    hints: hintsUsed,
  });

  scores.sort((a, b) => a.time - b.time);
  const top10 = scores.slice(0, 10);
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(top10));

  renderLeaderboard();
  hideModal();
  showMessage("Score saved to the leaderboard!", "success");
}

// ── Leaderboard ────────────────────────────────────────────────────────────

function getLeaderboard() {
  try {
    return JSON.parse(localStorage.getItem(LEADERBOARD_KEY)) || [];
  } catch {
    return [];
  }
}

function renderLeaderboard() {
  const tbody = document.getElementById("leaderboard-body");
  const scores = getLeaderboard();
  tbody.innerHTML = "";

  if (scores.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="5">No scores yet — complete a puzzle!</td>';
    tbody.appendChild(row);
    return;
  }

  scores.forEach((entry, i) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${i + 1}</td>
      <td>${escapeHtml(entry.name)}</td>
      <td>${formatTime(entry.time)}</td>
      <td>${escapeHtml(entry.level)}</td>
      <td>${entry.hints}</td>
    `;
    tbody.appendChild(row);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── Init ───────────────────────────────────────────────────────────────────

window.addEventListener("load", () => {
  initTheme();
  initBoardEventDelegation();
  renderLeaderboard();

  document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
  document.getElementById("new-game").addEventListener("click", newGame);
  document.getElementById("check-solution").addEventListener("click", checkSolution);
  document.getElementById("hint-btn").addEventListener("click", requestHint);
  document.getElementById("save-score").addEventListener("click", saveScore);
  document.getElementById("close-modal").addEventListener("click", hideModal);

  newGame();
});
