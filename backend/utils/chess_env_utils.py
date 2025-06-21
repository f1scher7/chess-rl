import chess
from backend.config import K_FACTOR


class ChessEnvUtils:

    @staticmethod
    def get_legal_action_idxs(board):
        legal_moves = list(board.legal_moves)
        legal_moves_idx = []

        for move in legal_moves:
            legal_moves_idx.append(ChessEnvUtils.get_move_idx(move=move))

        return legal_moves_idx


    @staticmethod
    def get_offset_move(move):
        if move.promotion:
            return 225 + (move.promotion - 2)  # move_str.promotion - 2 = skip pawn

        from_square = move.from_square  # idx of square
        to_square = move.to_square  # idx of square

        from_square_row, from_square_col = divmod(from_square, 8)
        to_square_row, to_square_col = divmod(to_square, 8)

        delta_row = to_square_row - from_square_row  # the min-max of delta_row is [-7, 7]
        delta_col = to_square_col - from_square_col  # the min-max of delta_col is [-7, 7]

        delta_row += 7  # avoid negative nums -> [0, 14]
        delta_col += 7  # avoid negative nums -> [0, 14]

        return delta_row * 15 + delta_col


    @staticmethod
    def get_move_idx(move):
        from_square = move.from_square

        move_offset = ChessEnvUtils.get_offset_move(move=move)

        return from_square * 73 + move_offset  # we have 73 because each square can have 4762 / 64 = 74.4 (73 idx)


    @staticmethod
    def update_elo(winner, white_elo, black_elo):
        expected_score_white = 1 / (1 + 10 ** ((black_elo - white_elo) / 400))  # chance of winning
        expected_score_black = 1 / (1 + 10 ** ((white_elo - black_elo) / 400))  # chance of winning

        if winner == chess.WHITE:
            white_elo += K_FACTOR * (1 - expected_score_white)
            black_elo += K_FACTOR * (0 - expected_score_black)
        elif winner == chess.BLACK:
            black_elo += K_FACTOR * (1 - expected_score_black)
            white_elo += K_FACTOR * (0 - expected_score_white)
        else:
            white_elo += K_FACTOR * (0.5 - expected_score_white)
            black_elo += K_FACTOR * (0.5 - expected_score_black)

        return white_elo, black_elo
