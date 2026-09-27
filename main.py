```python
# ============================================================
# CHESS 
WITH AI
# Pure Python - No External Libraries
# Black & White Chess Piece Theme
# AI: Minimax + Alpha-Beta Pruning
# ============================================================

import math

# ------------------------------------------------------------
# Chess Piece Display
# ------------------------------------------------------------

PIECES = {
    "K": "♔", "Q": "♕", "R": "♖",
    "B": "♗", "N": "♘", "P": "♙",

    "k": "♚", "q": "♛", "r": "♜",
    "b": "♝", "n": "♞", "p": "♟",

    ".": "·"
}

# ------------------------------------------------------------
# Starting Board
# ------------------------------------------------------------

STARTING_BOARD = [
    list("rnbqkbnr"),
    list("pppppppp"),
    list("........"),
    list("........"),
    list("........"),
    list("........"),
    list("PPPPPPPP"),
    list("RNBQKBNR")
]

PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 20000
}

KNIGHT_MOVES = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2), (1, 2),
    (2, -1), (2, 1)
]

KING_MOVES = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def inside(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def is_white(piece):
    return piece != "." and piece.isupper()


def is_black(piece):
    return piece != "." and piece.islower()


def same_color(p1, p2):
    if p1 == "." or p2 == ".":
        return False
    return p1.isupper() == p2.isupper()


def opponent(color):
    return "b" if color == "w" else "w"


def copy_board(board):
    return [row[:] for row in board]


def square_to_text(r, c):
    return chr(ord("a") + c) + str(8 - r)


def text_to_square(text):

    if len(text) != 2:
        return None

    if text[0] not in "abcdefgh":
        return None

    if text[1] not in "12345678":
        return None

    c = ord(text[0]) - ord("a")
    r = 8 - int(text[1])

    return r, c


# ============================================================
# DISPLAY BOARD
# ============================================================

def print_board(board):

    print()
    print("       a   b   c   d   e   f   g   h")
    print("     +---+---+---+---+---+---+---+---+")

    for r in range(8):

        pieces = []

        for c in range(8):
            pieces.append(PIECES[board[r][c]])

        print(
            f"  {8-r}  | "
            + " | ".join(pieces)
            + f" |  {8-r}"
        )

        print(
            "     +---+---+---+---+---+---+---+---+"
        )

    print("       a   b   c   d   e   f   g   h")
    print()


# ============================================================
# FIND KING
# ============================================================

def find_king(board, color):

    target = "K" if color == "w" else "k"

    for r in range(8):
        for c in range(8):

            if board[r][c] == target:
                return r, c

    return None


# ============================================================
# CHECK IF SQUARE IS ATTACKED
# ============================================================

def square_attacked(board, r, c, by_color):

    # ---------------- PAWNS ----------------

    if by_color == "w":

        pawn = "P"
        pawn_row = r + 1

        for dc in (-1, 1):

            if inside(pawn_row, c + dc):

                if board[pawn_row][c + dc] == pawn:
                    return True

    else:

        pawn = "p"
        pawn_row = r - 1

        for dc in (-1, 1):

            if inside(pawn_row, c + dc):

                if board[pawn_row][c + dc] == pawn:
                    return True

    # ---------------- KNIGHTS ----------------

    knight = "N" if by_color == "w" else "n"

    for dr, dc in KNIGHT_MOVES:

        nr = r + dr
        nc = c + dc

        if inside(nr, nc):

            if board[nr][nc] == knight:
                return True

    # ---------------- KING ----------------

    king = "K" if by_color == "w" else "k"

    for dr, dc in KING_MOVES:

        nr = r + dr
        nc = c + dc

        if inside(nr, nc):

            if board[nr][nc] == king:
                return True

    # ---------------- ROOK / QUEEN ----------------

    rook = "R" if by_color == "w" else "r"
    queen = "Q" if by_color == "w" else "q"

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        nr = r + dr
        nc = c + dc

        while inside(nr, nc):

            piece = board[nr][nc]

            if piece != ".":

                if piece == rook or piece == queen:
                    return True

                break

            nr += dr
            nc += dc

    # ---------------- BISHOP / QUEEN ----------------

    bishop = "B" if by_color == "w" else "b"

    directions = [
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1)
    ]

    for dr, dc in directions:

        nr = r + dr
        nc = c + dc

        while inside(nr, nc):

            piece = board[nr][nc]

            if piece != ".":

                if piece == bishop or piece == queen:
                    return True

                break

            nr += dr
            nc += dc

    return False


# ============================================================
# CHECK
# ============================================================

def in_check(board, color):

    king = find_king(board, color)

    if king is None:
        return True

    r, c = king

    return square_attacked(
        board,
        r,
        c,
        opponent(color)
    )


# ============================================================
# MOVE CLASS
# ============================================================

class Move:

    def __init__(
        self,
        start,
        end,
        promotion=None,
        castle=False,
        en_passant=False
    ):

        self.start = start
        self.end = end
        self.promotion = promotion
        self.castle = castle
        self.en_passant = en_passant

    def __repr__(self):

        return (
            square_to_text(*self.start)
            +
            square_to_text(*self.end)
        )


# ============================================================
# MAKE MOVE
# ============================================================

def make_move(board, move):

    new_board = copy_board(board)

    r1, c1 = move.start
    r2, c2 = move.end

    piece = new_board[r1][c1]

    new_board[r1][c1] = "."

    # En passant
    if move.en_passant:

        if piece == "P":
            new_board[r2 + 1][c2] = "."

        else:
            new_board[r2 - 1][c2] = "."

    # Promotion
    if move.promotion:

        if piece.isupper():
            piece = move.promotion.upper()
        else:
            piece = move.promotion.lower()

    new_board[r2][c2] = piece

    # Castling
    if move.castle:

        row = 7 if piece == "K" else 0

        # King side
        if c2 == 6:

            new_board[row][5] = new_board[row][7]
            new_board[row][7] = "."

        # Queen side
        elif c2 == 2:

            new_board[row][3] = new_board[row][0]
            new_board[row][0] = "."

    return new_board


# ============================================================
# GENERATE MOVES
# ============================================================

def generate_moves(board, color):

    moves = []

    for r in range(8):

        for c in range(8):

            piece = board[r][c]

            if piece == ".":
                continue

            if color == "w" and not piece.isupper():
                continue

            if color == "b" and not piece.islower():
                continue

            kind = piece.upper()

            # =================================================
            # PAWN
            # =================================================

            if kind == "P":

                direction = -1 if color == "w" else 1
                start_row = 6 if color == "w" else 1
                promotion_row = 0 if color == "w" else 7

                # Forward
                nr = r + direction

                if inside(nr, c) and board[nr][c] == ".":

                    if nr == promotion_row:

                        for promotion in "QRBN":

                            moves.append(
                                Move(
                                    (r, c),
                                    (nr, c),
                                    promotion
                                )
                            )

                    else:

                        moves.append(
                            Move(
                                (r, c),
                                (nr, c)
                            )
                        )

                    # Double move
                    nr2 = r + 2 * direction

                    if (
                        r == start_row
                        and board[nr2][c] == "."
                    ):

                        moves.append(
                            Move(
                                (r, c),
                                (nr2, c)
                            )
                        )

                # Captures
                for dc in (-1, 1):

                    nr = r + direction
                    nc = c + dc

                    if not inside(nr, nc):
                        continue

                    target = board[nr][nc]

                    if (
                        target != "."
                        and not same_color(piece, target)
                    ):

                        if nr == promotion_row:

                            for promotion in "QRBN":

                                moves.append(
                                    Move(
                                        (r, c),
                                        (nr, nc),
                                        promotion
                                    )
                                )

                        else:

                            moves.append(
                                Move(
                                    (r, c),
                                    (nr, nc)
                                )
                            )

            # =================================================
            # KNIGHT
            # =================================================

            elif kind == "N":

                for dr, dc in KNIGHT_MOVES:

                    nr = r + dr
                    nc = c + dc

                    if not inside(nr, nc):
                        continue

                    target = board[nr][nc]

                    if (
                        target == "."
                        or not same_color(piece, target)
                    ):

                        moves.append(
                            Move(
                                (r, c),
                                (nr, nc)
                            )
                        )

            # =================================================
            # KING
            # =================================================

            elif kind == "K":

                for dr, dc in KING_MOVES:

                    nr = r + dr
                    nc = c + dc

                    if not inside(nr, nc):
                        continue

                    target = board[nr][nc]

                    if (
                        target == "."
                        or not same_color(piece, target)
                    ):

                        moves.append(
                            Move(
                                (r, c),
                                (nr, nc)
                            )
                        )

                # Castling
                if not in_check(board, color):

                    row = 7 if color == "w" else 0

                    # King side
                    if (
                        board[row][5] == "."
                        and board[row][6] == "."
                    ):

                        rook = "R" if color == "w" else "r"

                        if board[row][7] == rook:

                            if (
                                not square_attacked(
                                    board,
                                    row,
                                    5,
                                    opponent(color)
                                )
                                and
                                not square_attacked(
                                    board,
                                    row,
                                    6,
                                    opponent(color)
                                )
                            ):

                                moves.append(
                                    Move(
                                        (r, c),
                                        (row, 6),
                                        castle=True
                                    )
                                )

                    # Queen side
                    if (
                        board[row][1] == "."
                        and board[row][2] == "."
                        and board[row][3] == "."
                    ):

                        rook = "R" if color == "w" else "r"

                        if board[row][0] == rook:

                            if (
                                not square_attacked(
                                    board,
                                    row,
                                    3,
                                    opponent(color)
                                )
                                and
                                not square_attacked(
                                    board,
                                    row,
                                    2,
                                    opponent(color)
                                )
                            ):

                                moves.append(
                                    Move(
                                        (r, c),
                                        (row, 2),
                                        castle=True
                                    )
                                )

            # =================================================
            # SLIDING PIECES
            # =================================================

            elif kind in ("B", "R", "Q"):

                directions = []

                if kind in ("B", "Q"):

                    directions += [
                        (-1, -1),
                        (-1, 1),
                        (1, -1),
                        (1, 1)
                    ]

                if kind in ("R", "Q"):

                    directions += [
                        (-1, 0),
                        (1, 0),
                        (0, -1),
                        (0, 1)
                    ]

                for dr, dc in directions:

                    nr = r + dr
                    nc = c + dc

                    while inside(nr, nc):

                        target = board[nr][nc]

                        if target == ".":

                            moves.append(
                                Move(
                                    (r, c),
                                    (nr, nc)
                                )
                            )

                        else:

                            if not same_color(
                                piece,
                                target
                            ):

                                moves.append(
                                    Move(
                                        (r, c),
                                        (nr, nc)
                                    )
                                )

                            break

                        nr += dr
                        nc += dc

    return moves


# ============================================================
# LEGAL MOVES
# ============================================================

def legal_moves(board, color):

    legal = []

    for move in generate_moves(board, color):

        new_board = make_move(board, move)

        if not in_check(new_board, color):
            legal.append(move)

    return legal


# ============================================================
# BOARD EVALUATION
# ============================================================

def evaluate(board):

    score = 0

    for row in board:

        for piece in row:

            if piece == ".":
                continue

            value = PIECE_VALUES[piece.upper()]

            if piece.isupper():
                score += value
            else:
                score -= value

    return score


# ============================================================
# MINIMAX + ALPHA BETA
# ============================================================

def minimax(
    board,
    depth,
    alpha,
    beta,
    maximizing
):

    if depth == 0:

        return evaluate(board), None

    color = "w" if maximizing else "b"

    moves = legal_moves(board, color)

    if not moves:

        if in_check(board, color):

            if maximizing:
                return -999999, None

            return 999999, None

        return 0, None

    best_move = None

    # --------------------------------------------------------
    # MAXIMIZING - WHITE
    # --------------------------------------------------------

    if maximizing:

        best_score = -math.inf

        for move in moves:

            new_board = make_move(board, move)

            score, _ = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                False
            )

            if score > best_score:

                best_score = score
                best_move = move

            alpha = max(alpha, score)

            if beta <= alpha:
                break

        return best_score, best_move

    # --------------------------------------------------------
    # MINIMIZING - BLACK
    # --------------------------------------------------------

    else:

        best_score = math.inf

        for move in moves:

            new_board = make_move(board, move)

            score, _ = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                True
            )

            if score < best_score:

                best_score = score
                best_move = move

            beta = min(beta, score)

            if beta <= alpha:
                break

        return best_score, best_move


# ============================================================
# USER MOVE PARSER
# ============================================================

def parse_move(text, moves):

    text = text.strip().lower()

    if len(text) not in (4, 5):
        return None

    start = text_to_square(text[:2])
    end = text_to_square(text[2:4])

    if start is None or end is None:
        return None

    promotion = None

    if len(text) == 5:

        promotion = text[4].upper()

        if promotion not in "QRBN":
            return None

    for move in moves:

        if (
            move.start == start
            and move.end == end
        ):

            if move.promotion:

                if promotion == move.promotion:
                    return move

            elif promotion is None:

                return move

    return None


# ============================================================
# MAIN GAME
# ============================================================

def play_game():

    board = copy_board(STARTING_BOARD)

    print()
    print("╔══════════════════════════════════════╗")
    print("║          ♔ CHESS WITH AI ♚          ║")
    print("╚══════════════════════════════════════╝")

    print()
    print("You  : ♙ WHITE")
    print("AI   : ♟ BLACK")
    print()
    print("Enter moves like: e2e4")
    print("Promotion example: e7e8q")
    print("Type 'quit' to exit.")
    print()

    turn = "w"

    while True:

        print_board(board)

        moves = legal_moves(board, turn)

        # Checkmate / stalemate
        if not moves:

            if in_check(board, turn):

                if turn == "w":
                    print("♚ CHECKMATE — AI WINS!")

                else:
                    print("♔ CHECKMATE — YOU WIN!")

            else:

                print("DRAW — STALEMATE!")

            break

        if in_check(board, turn):
            print("⚠ CHECK!")

        # ====================================================
        # PLAYER
        # ====================================================

        if turn == "w":

            command = input("♔ Your move: ")

            if command.lower() == "quit":

                print("Game ended.")
                break

            move = parse_move(
                command,
                moves
            )

            if move is None:

                print("❌ Invalid move.")
                print("Example: e2e4")
                continue

            board = make_move(
                board,
                move
            )

            turn = "b"

        # ====================================================
        # AI
        # ====================================================

        else:

            print("♚ AI is thinking...")

            # Change to 4 for stronger AI
            depth = 3

            score, ai_move = minimax(
                board,
                depth,
                -math.inf,
                math.inf,
                False
            )

            if ai_move is None:
                break

            print(
                "♚ AI move:",
                square_to_text(*ai_move.start)
                +
                square_to_text(*ai_move.end)
            )

            board = make_move(
                board,
                ai_move
            )

            turn = "w"


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    play_game()
```
