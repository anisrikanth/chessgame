import random

class ChessEngine:
    def __init__(self):
        # Represent chessboard, lowercase is black, uppercase is white, . = empty space
        self.board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ]
        self.white_turn = True
        self.game_over = False
        
        # Base values multiplied by 10 to allow for integer positional bonuses
        self.piece_values = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}
        
        # Mapping unicode symbols for black and white chess pieces
        self.unicode_pieces = {
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            '.': '·'
        }

    def describe_move(self, start, end):
        """Generate a text description of the move"""
        piece_char = self.board[start[0]][start[1]]
        target_char = self.board[end[0]][end[1]]
        
        names = {'P': 'Pawn', 'N': 'Knight', 'B': 'Bishop', 'R': 'Rook', 'Q': 'Queen', 'K': 'King'}
        
        color = "White" if piece_char.isupper() else "Black"
        p_name = names.get(piece_char.upper(), "Piece")
        
        cols = "abcdefgh"
        end_sq = f"{cols[end[1]]}{8-end[0]}"
        
        desc = f"{color} {p_name} to {end_sq}."
        
        if target_char != ".":
            cap_name = names.get(target_char.upper(), "Piece")
            desc += f" Captures {cap_name}!"
            
        return desc

    def print_board(self):
        """Prints the board to the console with ranks, files, and unicode pieces"""
        print("\n  a b c d e f g h")
        for r in range(8):
            row = f"{8 - r} "
            for c in range(8):
                piece = self.board[r][c]
                symbol = self.unicode_pieces.get(piece, piece)
                row += symbol + " "
            print(row)

    def parse_pos(self, txt):
        """Convert algebraic notation to (row, col) tuple indices"""
        try:
            col, row = ord(txt[0]) - 97, 8 - int(txt[1])
            if 0 <= col <= 7 and 0 <= row <= 7:
                return row, col
        except:
            pass
        return None

    def on_board(self, r, c):
        """Checks if the coordinates are within the board boundaries"""
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece(self, r, c):
        """Returns the character as the specific board location"""
        return self.board[r][c]

    def is_enemy(self, r, c, is_white):
        """Returns true if the piece at (row, col) is an enemy piece"""
        p = self.get_piece(r, c)
        if p == ".":
            return False
        return p.islower() if is_white else p.isupper()

    def get_all_moves(self, board, is_white):
        """Generates all pseudo-legal moves for the given color"""
        moves = []
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p == "." or (p.isupper() != is_white):
                    continue
                
                piece_type = p.upper()
                directions = []
                
                if piece_type == "P":
                    dr = -1 if is_white else 1

                    # Move forward 1
                    if self.on_board(r+dr, c) and board[r+dr][c] == ".":
                        moves.append(((r, c), (r+dr, c)))
                        
                        # Move forward 2 (but only from starting rank)
                        start_row = 6 if is_white else 1
                        if r == start_row and board[r+(dr*2)][c] == ".":
                            moves.append(((r, c), (r+(dr*2), c)))
                    
                    # Captures
                    for dc in [-1, 1]:
                        if self.on_board(r+dr, c+dc):
                            target = board[r+dr][c+dc]
                            if target != "." and (target.islower() if is_white else target.isupper()):
                                moves.append(((r, c), (r+dr, c+dc)))

                elif piece_type == "N":
                    jumps = [(r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1),
                             (r+1, c+2), (r+1, c-2), (r-1, c+2), (r-1, c-2)]
                    for tr, tc in jumps:
                        if self.on_board(tr, tc):
                            target = board[tr][tc]
                            if target == "." or (target.islower() if is_white else target.isupper()):
                                moves.append(((r, c), (tr, tc)))

                elif piece_type == "K":
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            if self.on_board(r+dr, c+dc):
                                target = board[r+dr][c+dc]
                                if target == "." or (target.islower() if is_white else target.isupper()):
                                    moves.append(((r, c), (r+dr, c+dc)))
                
                # Sliding pieces (B, R, Q)
                else:
                    if piece_type in ["B", "Q"]:
                        directions.extend([(1,1), (1,-1), (-1,1), (-1,-1)])
                    if piece_type in ["R", "Q"]:
                        directions.extend([(1,0), (-1,0), (0,1), (0,-1)])
                    
                    for dr, dc in directions:
                        tr, tc = r + dr, c + dc
                        while self.on_board(tr, tc):
                            target = board[tr][tc]
                            if target == ".":
                                moves.append(((r, c), (tr, tc)))
                            else:
                                if target.islower() if is_white else target.isupper():
                                    moves.append(((r, c), (tr, tc)))
                                break 
                            tr, tc = tr + dr, tc + dc
        return moves

    def make_move(self, board, move):
        """Returns a new board state after making the given move (handles promotion)"""
        new_board = [row[:] for row in board]
        start, end = move
        piece = new_board[start[0]][start[1]]
        new_board[end[0]][end[1]] = piece
        new_board[start[0]][start[1]] = "."
        
        # Check for Pawn promotion
        if piece.upper() == "P":
            if (piece.isupper() and end[0] == 0) or (piece.islower() and end[0] == 7):
                # Always promote to Queen for simplicity
                new_board[end[0]][end[1]] = "Q" if piece.isupper() else "q"
        return new_board

    def is_in_check(self, board, is_white):
        """Returns True if the current player's king is in check"""
        king_char = "K" if is_white else "k"
        king_pos = None
        for r in range(8):
            for c in range(8):
                if board[r][c] == king_char:
                    king_pos = (r, c)
                    break
        if not king_pos:
            return True

        enemy_moves = self.get_all_moves(board, not is_white)
        for _, end in enemy_moves:
            if end == king_pos:
                return True
        return False

    def get_valid_moves(self, board, is_white):
        """Generates moves and filters out those that leave king in check"""
        pseudo_moves = self.get_all_moves(board, is_white)
        valid_moves = []
        for move in pseudo_moves:
            future_board = self.make_move(board, move)
            if not self.is_in_check(future_board, is_white):
                valid_moves.append(move)
        return valid_moves

    def get_position_bonus(self, piece, r, c):
        """Returns a small bonus for good positioning (either center control or advancing)"""
        bonus = 0
        p_type = piece.upper()
        
        # Center squares (d4, d5, e4, e5) worth more
        is_center = (3 <= r <= 4) and (3 <= c <= 4)
        is_extended_center = (2 <= r <= 5) and (2 <= c <= 5)
        
        if p_type == "P":
            # Encourage advancing
            rank = (7-r) if piece.isupper() else r
            bonus += rank * 0.1 # Push forward
            if is_center:
                bonus += 0.3
            
        elif p_type == "N":
            if is_center:
                bonus += 0.5
            elif is_extended_center:
                bonus += 0.2
            
        elif p_type == "B":
            if is_extended_center:
                bonus += 0.2
        
         # Don't bring Queen out too early
        elif p_type == "Q":
            if is_center:
                bonus += 0.1
            
        elif p_type == "K":
            # Keep King back in early game
            rank = (7-r) if piece.isupper() else r
            if rank < 1:
                bonus += 0.3
            
        return bonus

    def evaluate_board(self, board):
        """Calculates a score for the board from White's perspective"""
        score = 0
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p == ".":
                    continue
                
                # Material Value
                val = self.piece_values.get(p.upper(), 0)
                
                # Positional Value
                pos_bonus = self.get_position_bonus(p, r, c)
                
                if p.isupper():
                    score += (val + pos_bonus)
                else:
                    score -= (val + pos_bonus)
        return score

    def minimax(self, board, depth, maximizing_player):
        """Minimax algorithm to find optmial move by simulating future states"""
        if depth == 0:
            return self.evaluate_board(board), None

        valid_moves = self.get_valid_moves(board, maximizing_player)
        
        # Shuffle to prevent identical games and break tie-breakers randomly
        random.shuffle(valid_moves)
        
        if not valid_moves:
            if self.is_in_check(board, maximizing_player):
                # Checkmate
                return (-10000 if maximizing_player else 10000), None 
            return 0, None # Stalemate

        # Fallback move
        best_move = random.choice(valid_moves)

        if maximizing_player:
            max_eval = -float('inf')
            for move in valid_moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth-1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth-1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

if __name__ == "__main__":
    game = ChessEngine()
    print("Welcome to Python Chess.")
    print("You are White. AI is Black.")
    print("Enter moves as 'e2 e4'.")

    while not game.game_over:
        game.print_board()
        
        if game.white_turn:
            valid_moves = game.get_valid_moves(game.board, True)
            if not valid_moves:
                if game.is_in_check(game.board, True):
                    print("Checkmate! Black wins.")
                    break
                else:
                    print("Stalemate!")
                    break
            
            move_str = input("Your Move: ").strip().split()
            if len(move_str) != 2:
                continue
            
            start, end = game.parse_pos(move_str[0]), game.parse_pos(move_str[1])
            if start and end and ((start, end) in valid_moves):
                print(f"> {game.describe_move(start, end)}")
                game.board = game.make_move(game.board, (start, end))
                game.white_turn = False
                if game.is_in_check(game.board, False):
                    print("Check!")
            else:
                print("Invalid move. Try again.")
        else:
            print("AI's turn...")
            valid_moves = game.get_valid_moves(game.board, False)
            if not valid_moves:
                if game.is_in_check(game.board, False):
                    print("Checkmate! White wins.")
                    break
                else:
                    print("Stalemate!")
                    break
            
            _, ai_move = game.minimax(game.board, 2, False) 

            print(f"> {game.describe_move(ai_move[0], ai_move[1])}")
            game.board = game.make_move(game.board, ai_move)
            game.white_turn = True
            
            if game.is_in_check(game.board, True):
                print("Check!")
