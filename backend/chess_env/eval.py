import chess


class Eval:

    @staticmethod
    def evaluate_material(board):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        evaluation = 0

        for square, piece in board.piece_map().items():
            value = piece_values.get(piece.type)

            evaluation += value if piece.color == chess.WHITE else -value

        return evaluation


    @staticmethod
    def evaluate_mobility(board):
        curr_turn = board.turn
        first_player_moves = len(list(board.legal_moves))

        board.turn = not curr_turn
        second_player_moves = len(list(board.legal_moves))

        board.turn = curr_turn

        if board.turn:
            return first_player_moves - second_player_moves
        else:
            return second_player_moves - first_player_moves


    @staticmethod
    def evaluate_king_safety(board):
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        white_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[white_king])
            if board.piece_at(sq) is not None and board.piece_at(sq).color == chess.WHITE
        )

        black_king_safety = sum(
            1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[black_king])
            if board.piece_at(sq) is not None and board.piece_at(sq).color == chess.WHITE
        )

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
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)

        def count_weak_pawns(pawn_set):
            weak_pawns = 0

            # columns
            files = [chess.square_file(sq) for sq in pawn_set]
            files_pawn_counter = {f: files.count(f) for f in set(files)}

            for i in range(len(files) - 1):
                if files[i] + 1 != files[i + 1] and files[i] != files[i + 1]:
                    weak_pawns += 1

            weak_pawns += sum(pawn_num > 1 for pawn_num in files_pawn_counter.values())

            return weak_pawns

        return - (count_weak_pawns(white_pawns) - (count_weak_pawns(black_pawns)))


    @staticmethod
    def evaluate_board(board):
        # weights
        w1, w2, w3, w4, w5 = 1.0, 0.5, 0.5, 0.3, 0.3

        evaluation = (
            w1 * Eval.evaluate_material(board) +
            w2 * Eval.evaluate_mobility(board) +
            w3 * Eval.evaluate_king_safety(board) +
            w4 * Eval.evaluate_center_control(board) +
            w5 * Eval.evaluate_pawn_structure(board)
        )

        return evaluation