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


    def __init__(self, board):
        self.board = board

        self.white_castling_reward_given = False
        self.black_castling_reward_given = False


    def evaluate_board(self):
        # weights
        w1, w2, w3, w4, w5, w6 = 2.0, 1.0, 1, 0.75, 0.5, 0.5

        evaluation = (
            w1 * self.evaluate_material() +
            w2 * self.evaluate_threats() +
            w3 * self.evaluate_king_safety() +
            w4 * self.evaluate_mobility() +
            w5 * self.evaluate_center_control() +
            w6 * self.evaluate_pawn_structure()
        )

        return evaluation


    def evaluate_material(self):
        evaluation = 0

        for square, piece in self.board.piece_map().items():
            value = Eval.piece_values.get(piece.piece_type)

            evaluation += value if piece.color == chess.WHITE else -value

        return evaluation


    def evaluate_threats(self):
        def push_square_to_list(legal_moves_f, from_sq_f, to_sq_f, list_f):
            move_f = chess.Move(from_square=from_sq_f, to_square=to_sq_f)

            if move_f in legal_moves_f:
                board_copy_f = self.board.copy()
                board_copy_f.push(move_f)

                if not board_copy_f.is_check():
                    list_f.append(from_sq_f)

            return list_f

        evaluation = 0
        legal_moves = set(self.board.legal_moves)

        for to_sq, piece in self.board.piece_map().items():
            sign = 1 if self.board.piece_at(to_sq).color == chess.WHITE else -1

            attackers = []
            for from_sq in self.board.attackers(not piece.color, to_sq):
                attackers = push_square_to_list(legal_moves_f=legal_moves, from_sq_f=from_sq, to_sq_f=to_sq, list_f=attackers)

            defenders = []
            for from_sq in self.board.attackers(piece.color, to_sq):
                defenders = push_square_to_list(legal_moves_f=legal_moves, from_sq_f=from_sq, to_sq_f=to_sq, list_f=attackers)


            if not attackers:
                continue

            curr_piece_value = Eval.piece_values.get(piece.piece_type)

            if not defenders:
                evaluation -= curr_piece_value * sign
                continue

            attackers_value_sum = self.get_pieces_value_sum_by_squares(squares=attackers)
            defenders_value_sum = self.get_pieces_value_sum_by_squares(squares=defenders)

            avg_attackers_value = attackers_value_sum / len(attackers)

            if attackers_value_sum <= defenders_value_sum and len(attackers) > len(defenders) and avg_attackers_value < curr_piece_value:
                potential_loss = curr_piece_value - avg_attackers_value

                if potential_loss > 0:
                    evaluation -= potential_loss * sign

        return evaluation


    def evaluate_mobility(self):
        board_copy = self.board.copy()

        board_copy.turn = chess.WHITE
        white_player_moves = len(list(board_copy.legal_moves))

        board_copy.turn = chess.BLACK
        black_player_moves = len(list(board_copy.legal_moves))

        return white_player_moves - black_player_moves


    def evaluate_king_safety(self):
        white_king = self.board.king(chess.WHITE)
        black_king = self.board.king(chess.BLACK)

        white_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[white_king])
            if self.board.piece_at(sq) is not None and self.board.piece_at(sq).color == chess.WHITE
        ) / 2

        black_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[black_king])
            if self.board.piece_at(sq) is not None and self.board.piece_at(sq).color == chess.BLACK
        ) / 2

        if len(self.board.move_stack) >= 2:
            last_move = self.board.move_stack[-1]

            if self.board.piece_at(last_move.to_square).color == chess.WHITE and not self.white_castling_reward_given:
                if self.board.is_castling(last_move):
                    white_king_safety += CASTLING_BONUS
                    self.white_castling_reward_given = True
                elif not self.board.has_castling_rights(chess.WHITE):
                    white_king_safety -= CASTLING_BONUS
                    self.white_castling_reward_given = True

            elif self.board.piece_at(last_move.to_square).color == chess.BLACK and not self.black_castling_reward_given:
                if self.board.is_castling(last_move):
                    black_king_safety += CASTLING_BONUS
                    self.black_castling_reward_given = True
                elif not self.board.has_castling_rights(chess.BLACK):
                    black_king_safety -= CASTLING_BONUS
                    self.black_castling_reward_given = True

        return white_king_safety - black_king_safety


    def evaluate_center_control(self):
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]

        white_control = 0
        black_control = 0

        for sq in center_squares:
            white_control += len(self.board.attackers(chess.WHITE, sq))
            black_control += len(self.board.attackers(chess.BLACK, sq))

        return white_control - black_control


    def evaluate_pawn_structure(self):
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

        white_weak_pawns = count_weak_pawns(self.board.pieces(chess.PAWN, chess.WHITE))
        black_weak_pawns = count_weak_pawns(self.board.pieces(chess.PAWN, chess.BLACK))

        return black_weak_pawns - white_weak_pawns


    def evaluate_capture_decision(self, move_played):
        mover_piece = self.board.piece_at(move_played.from_square)
        mover_color = mover_piece.color

        reward_or_penalty = 0
        good_captures_list = []

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                piece_captured = self.board.piece_at(move.to_square)
                piece_moving = self.board.piece_at(move.from_square)

                if not piece_captured or not piece_moving or piece_captured.color == mover_color:
                    continue

                board_copy = self.board.copy()
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


    def get_pieces_value_sum_by_squares(self, squares):
        return sum(
            Eval.piece_values.get(self.board.piece_at(sq).piece_type)
            for sq in squares if self.board.piece_at(sq)
        )


    def reset_castling_rewards(self):
        self.white_castling_reward_given = False
        self.black_castling_reward_given = False
