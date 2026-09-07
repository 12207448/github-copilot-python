import random

import pytest

import sudoku_logic


def count_clues(board):
    return sum(
        cell != sudoku_logic.EMPTY
        for row in board
        for cell in row
    )


def is_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))

    for index in range(sudoku_logic.SIZE):
        if set(board[index]) != expected:
            return False
        if {board[row][index] for row in range(sudoku_logic.SIZE)} != expected:
            return False

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_col in range(0, sudoku_logic.SIZE, 3):
            box = {
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            }
            if box != expected:
                return False

    return True


def test_create_empty_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(
        cell == sudoku_logic.EMPTY
        for row in board
        for cell in row
    )


def test_is_safe_valid_cell_placement():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 3)
    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)


def test_fill_board_generates_complete_valid_board():
    random.seed(0)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert is_valid_solution(board)


def test_generated_puzzle_has_unique_solution():
    random.seed(0)
    puzzle, solution = sudoku_logic.generate_puzzle("medium")

    assert is_valid_solution(solution)
    assert sudoku_logic.has_unique_solution(puzzle)


def test_difficulty_levels_produce_different_clue_counts():
    random.seed(0)
    easy, _ = sudoku_logic.generate_puzzle("easy")
    medium, _ = sudoku_logic.generate_puzzle("medium")
    hard, _ = sudoku_logic.generate_puzzle("hard")

    clue_counts = [count_clues(easy), count_clues(medium), count_clues(hard)]

    assert clue_counts == [
        sudoku_logic.DIFFICULTY_CLUES["easy"],
        sudoku_logic.DIFFICULTY_CLUES["medium"],
        sudoku_logic.DIFFICULTY_CLUES["hard"],
    ]
    assert clue_counts[0] > clue_counts[1] > clue_counts[2]


def test_find_conflicts_detects_duplicate_cells():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][3] = 5
    board[1][0] = 5

    conflicts = {tuple(cell) for cell in sudoku_logic.find_conflicts(board)}

    assert {(0, 0), (0, 3), (1, 0)} <= conflicts


def test_find_incorrect_cells():
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = 9

    incorrect = sudoku_logic.find_incorrect_cells(board, solution)

    assert [0, 0] in incorrect


def test_count_solutions_finds_single_solution():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle), limit=2) == 1


def test_find_hint_cell_returns_an_empty_cell_and_solution_value():
    random.seed(0)
    puzzle, solution = sudoku_logic.generate_puzzle("easy")

    hint = sudoku_logic.find_hint_cell(puzzle, solution)

    assert hint is not None
    row, col, value = hint
    assert puzzle[row][col] == sudoku_logic.EMPTY
    assert value == solution[row][col]
    assert sudoku_logic.find_hint_cell(solution, solution) is None


def test_invalid_difficulty_raises_value_error():
    with pytest.raises(ValueError, match="Unknown difficulty"):
        sudoku_logic.generate_puzzle("impossible")
