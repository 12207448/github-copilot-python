"""Sudoku puzzle generation, validation, and solving logic."""

import copy
import random
from typing import List, Optional, Tuple

SIZE = 9
EMPTY = 0

DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 35,
    "hard": 28,
}

Board = List[List[int]]


def deep_copy(board: Board) -> Board:
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Return True if placing num at (row, col) does not violate Sudoku rules."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board: Board) -> bool:
    """Fill an empty board with a complete valid solution using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions up to limit; used to verify a puzzle has a unique solution."""
    empty_cell = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                empty_cell = (row, col)
                break
        if empty_cell:
            break

    if empty_cell is None:
        return 1

    row, col = empty_cell
    count = 0
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            count += count_solutions(board, limit)
            board[row][col] = EMPTY
            if count >= limit:
                return count
    return count


def has_unique_solution(board: Board) -> bool:
    """Return True when the board has exactly one solution."""
    board_copy = deep_copy(board)
    return count_solutions(board_copy, limit=2) == 1


def remove_cells(solution: Board, clues: int) -> Board:
    """
    Remove cells from a complete solution while preserving a unique solution.

    Each candidate removal is checked with the solution counter. The counter
    stops after finding two solutions, so a removal is accepted only when the
    resulting puzzle still has exactly one solution.
    """
    puzzle = deep_copy(solution)
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    current_clues = sum(1 for r in range(SIZE) for c in range(SIZE) if puzzle[r][c] != EMPTY)

    for row, col in cells:
        if current_clues <= clues:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = EMPTY

        # count_solutions backtracks in place, so count on an isolated copy.
        if count_solutions(deep_copy(puzzle), limit=2) != 1:
            puzzle[row][col] = backup
        else:
            current_clues -= 1

    return puzzle


def generate_puzzle(difficulty: str = "medium") -> Tuple[Board, Board]:
    """
    Generate a Sudoku puzzle and its solution for the given difficulty level.
    Raises ValueError for unknown difficulty.
    """
    clues = DIFFICULTY_CLUES.get(difficulty)
    if clues is None:
        raise ValueError(f"Unknown difficulty: {difficulty}. Use easy, medium, or hard.")

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    puzzle = remove_cells(solution, clues)
    return puzzle, solution


def find_incorrect_cells(board: Board, solution: Board) -> List[List[int]]:
    """Return coordinates of cells that differ from the correct solution."""
    incorrect = []
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY and board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect


def find_conflicts(board: Board) -> List[List[int]]:
    """
    Return coordinates of cells involved in rule violations (duplicate in row/col/box).
    Used for immediate live feedback on the client side (also available server-side).
    """
    conflicts: set[tuple[int, int]] = set()

    for row in range(SIZE):
        seen: dict[int, list[tuple[int, int]]] = {}
        for col in range(SIZE):
            val = board[row][col]
            if val == EMPTY:
                continue
            if val in seen:
                for pos in seen[val]:
                    conflicts.add(pos)
                conflicts.add((row, col))
            else:
                seen[val] = [(row, col)]

    for col in range(SIZE):
        seen: dict[int, list[tuple[int, int]]] = {}
        for row in range(SIZE):
            val = board[row][col]
            if val == EMPTY:
                continue
            if val in seen:
                for pos in seen[val]:
                    conflicts.add(pos)
                conflicts.add((row, col))
            else:
                seen[val] = [(row, col)]

    for box_row in range(3):
        for box_col in range(3):
            seen: dict[int, list[tuple[int, int]]] = {}
            for i in range(3):
                for j in range(3):
                    row = box_row * 3 + i
                    col = box_col * 3 + j
                    val = board[row][col]
                    if val == EMPTY:
                        continue
                    if val in seen:
                        for pos in seen[val]:
                            conflicts.add(pos)
                        conflicts.add((row, col))
                    else:
                        seen[val] = [(row, col)]

    return [[r, c] for r, c in conflicts]


def find_hint_cell(board: Board, solution: Board) -> Optional[List[int]]:
    """Return [row, col, value] for one empty cell, or None if the board is full."""
    empty_cells = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] == EMPTY
    ]
    if not empty_cells:
        return None
    row, col = random.choice(empty_cells)
    return [row, col, solution[row][col]]


def is_board_complete(board: Board, solution: Board) -> bool:
    """Return True when every cell matches the solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != solution[row][col]:
                return False
    return True
