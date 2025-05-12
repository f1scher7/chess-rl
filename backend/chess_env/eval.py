import chess
from backend.config import CASTLING_BONUS


class Eval:

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    white_castling_reward_given = False
    black_castling_reward_given = False


    @staticmethod
    def evaluate_board(board):
        # weights
        w1, w2, w3, w4, w5, w6 = 2.0, 1.0, 1, 0.75, 0.5, 0.5

        evaluation = (
            w1 * Eval.evaluate_material(board) +
            w2 * Eval.evaluate_threats(board) +
            w3 * Eval.evaluate_king_safety(board) +
            w4 * Eval.evaluate_mobility(board) +
            w5 * Eval.evaluate_center_control(board) +
            w6 * Eval.evaluate_pawn_structure(board)
        )

        return evaluation


    @staticmethod
    def evaluate_material(board):
        evaluation = 0

        for square, piece in board.piece_map().items():
            value = Eval.piece_values.get(piece.piece_type)

            evaluation += value if piece.color == chess.WHITE else -value

        return evaluation


    @staticmethod
    def evaluate_threats(board):
        evaluation = 0
        legal_moves = set(board.legal_moves)

        for square, piece in board.piece_map().items():
            sign = 1 if board.piece_at(square).color == chess.WHITE else -1

            attackers = []
            for sq in board.attackers(not piece.color, square):
                move = chess.Move(from_square=sq, to_square=square)
                if move in legal_moves:
                    board_copy = board.copy()
                    board_copy.push(move)
                    if not board_copy.is_check():
                        attackers.append(sq)

            defenders = []
            for sq in board.attackers(piece.color, square):
                move = chess.Move(from_square=sq, to_square=square)
                if move in legal_moves:
                    board_copy = board.copy()
                    board_copy.push(move)
                    if not board_copy.is_check():
                        defenders.append(sq)

            if not attackers:
                continue

            curr_piece_value = Eval.piece_values.get(piece.piece_type)

            if not defenders:
                evaluation -= curr_piece_value * sign
                continue

            attackers_value_sum = Eval.get_pieces_value_sum_by_squares(board=board, squares=attackers)
            defenders_value_sum = Eval.get_pieces_value_sum_by_squares(board=board, squares=defenders)

            avg_attackers_value = attackers_value_sum / len(attackers)

            if attackers_value_sum <= defenders_value_sum and len(attackers) > len(defenders) and avg_attackers_value < curr_piece_value:
                potential_loss = curr_piece_value - avg_attackers_value

                if potential_loss > 0:
                    evaluation -= potential_loss * sign

        return evaluation


    @staticmethod
    def evaluate_mobility(board):
        board_copy = board.copy()

        board_copy.turn = chess.WHITE
        white_player_moves = len(list(board_copy.legal_moves))

        board_copy.turn = chess.BLACK
        black_player_moves = len(list(board_copy.legal_moves))

        return white_player_moves - black_player_moves


    @staticmethod
    def evaluate_king_safety(board):
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        white_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[white_king])
            if board.piece_at(sq) is not None and board.piece_at(sq).color == chess.WHITE
        ) / 2

        black_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[black_king])
            if board.piece_at(sq) is not None and board.piece_at(sq).color == chess.BLACK
        ) / 2

        if len(board.move_stack) >= 2:
            last_move = board.move_stack[-1]

            if board.piece_at(last_move.to_square).color == chess.WHITE and not Eval.white_castling_reward_given:
                if board.is_castling(last_move):
                    white_king_safety += CASTLING_BONUS
                    Eval.white_castling_reward_given = True
                elif not board.has_castling_rights(chess.WHITE):
                    white_king_safety -= CASTLING_BONUS
                    Eval.white_castling_reward_given = True

            elif board.piece_at(last_move.to_square).color == chess.BLACK and not Eval.black_castling_reward_given:
                if board.is_castling(last_move):
                    black_king_safety += CASTLING_BONUS
                    Eval.black_castling_reward_given = True
                elif not board.has_castling_rights(chess.BLACK):
                    black_king_safety -= CASTLING_BONUS
                    Eval.black_castling_reward_given = True

        return white_king_safety - black_king_safety


    @staticmethod
    def evaluate_center_control(board):
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]

        white_control = 0
        black_control = 0

        for sq in center_squares:
            white_control += len(board.attackers(chess.WHITE, sq))
            black_control += len(board.attackers(chess.BLACK, sq))

        return white_control - black_control


    @staticmethod
    def evaluate_pawn_structure(board):
        def count_weak_pawns(pawns):
            weak_pawns = 0

            for square in pawns:
                file = chess.square_file(square)

                has_left_neighbours = any(
                    chess.square_file(sq) == file - 1
                    for sq in pawns if sq != square
                )

                has_right_neighbours = any(
                    chess.square_file(sq) == file + 1
                    for sq in pawns if sq != square
                )

                if not has_right_neighbours and not has_left_neighbours:
                    weak_pawns += 1

                same_file_pawns = [
                    sq for sq in pawns
                    if chess.square_file(sq) == file and sq != square
                ]

                if same_file_pawns:
                    weak_pawns += len(same_file_pawns) - 1

            return weak_pawns

        white_weak_pawns = count_weak_pawns(board.pieces(chess.PAWN, chess.WHITE))
        black_weak_pawns = count_weak_pawns(board.pieces(chess.PAWN, chess.BLACK))

        return black_weak_pawns - white_weak_pawns


    @staticmethod
    def evaluate_capture_decision(board, move_played):
        mover_piece = board.piece_at(move_played.from_square)
        mover_color = mover_piece.color

        reward_or_penalty = 0
        good_captures_list = []

        for move in board.legal_moves:
            if board.is_capture(move):
                piece_captured = board.piece_at(move.to_square)
                piece_moving = board.piece_at(move.from_square)

                if not piece_captured or not piece_moving or piece_captured.color == mover_color:
                    continue

                board_copy = board.copy()
                board_copy.push(move)

                if board_copy.is_check():
                    continue

                gain = Eval.piece_values.get(piece_captured.piece_type) - Eval.piece_values.get(piece_moving.piece_type)

                if gain > 1:
                    good_captures_list.append((move, gain))

        if good_captures_list:
            best_move, best_gain = max(good_captures_list, key=lambda x: x[1])

            if move_played not in [m for m, _ in good_captures_list]:
                reward_or_penalty -= best_gain
            else:
                reward_or_penalty += best_gain

        return reward_or_penalty


    @staticmethod
    def get_pieces_value_sum_by_squares(board, squares):
        return sum(
            Eval.piece_values.get(board.piece_at(sq).piece_type)
            for sq in squares if board.piece_at(sq)
        )


    @staticmethod
    def reset_castling_rewards():
        Eval.white_castling_reward_given = False
        Eval.black_castling_reward_given = False
