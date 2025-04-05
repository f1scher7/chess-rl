import chess
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from backend.config import WHITE_ELO, BLACK_ELO, K_FACTOR
from backend.utils.chess_env_utils import get_offset_move, get_move_index


class ChessEnv(gym.Env):

    def __init__(self):
        super(ChessEnv, self).__init__()

        self.board = chess.Board()
        self.white_elo = WHITE_ELO
        self.black_elo = BLACK_ELO

        self.action_space = spaces.Discrete(4672)  # all possible moves for each piece
        self.observation_space = spaces.Box(0, 1, shape=(8, 8, 12),
                                            dtype=np.float32)  # 12 = all white pieces [0:6] and black pieces [6:12]

    def step(self, action_no):
        move = self.decode_action(action_no=action_no)

        self.board.push(move)

        white_reward, black_reward, done = self.get_reward()

        observation = self.get_observation(board=self.board)

        info = {'board_fen': self.board.fen()}

        return observation, (white_reward, black_reward), done, info

    def get_reward(self):
        if self.board.is_checkmate():
            winner_color = 'white' if self.board.turn == chess.BLACK else 'black'

            if winner_color == 'white':
                white_reward, black_reward = 1, -1
            else:
                white_reward, black_reward = -1, 1

            self.update_elo(winner_color=winner_color)

            return white_reward, black_reward, True

        elif self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.can_claim_threefold_repetition() or self.board.is_fivefold_repetition():
            self.update_elo('draw')
            return 0, 0, True

        return 0, 0, False

    @staticmethod
    def get_observation(board):
        observation = np.zeros((8, 8, 12), dtype=np.float32)

        piece_map = {
            chess.PAWN: 0,
            chess.KNIGHT: 1,
            chess.BISHOP: 2,
            chess.ROOK: 3,
            chess.QUEEN: 4,
            chess.KING: 5,
        }

        for square, piece in board.piece_map().items():
            row, col = divmod(square,
                              8)  # getting the coordinate from the square number e.g.: we have square no. 10 so we have  10 // 8 and 10 % 8  = (1, 2) =  B3
            piece_type = piece_map[piece.piece_type]

            if piece.color == chess.WHITE:
                observation[row, col, piece_type] = 1
            else:
                observation[row, col, piece_type + 6] = 1

        return observation

    def get_legal_actions_idx(self):
        legal_moves = list(self.board.legal_moves)
        legal_moves_idx = []

        for move in legal_moves:
            legal_moves_idx.append(get_move_index(move=move))

        return legal_moves_idx

    def decode_action(self, action_no):
        # Decode the number of action to legal chess move e.g. e4, because AI choose only the number of action
        legal_moves = list(self.board.legal_moves)
        return legal_moves[action_no]

    def reset(self, seed=None, options=None):
        self.board.reset()
        return self.get_observation(board=self.board), {}  # we should also return info dict but for now its empty :D

    def update_elo(self, winner_color):
        expected_score_white = 1 / (1 + 10 ** ((self.black_elo - self.white_elo) / 400))  # chance of winning
        expected_score_black = 1 / (1 + 10 ** ((self.white_elo - self.black_elo) / 400))  # chance of winning

        if winner_color == 'white':
            self.white_elo += K_FACTOR * (1 - expected_score_white)
            self.black_elo += K_FACTOR * (0 - expected_score_black)
        elif winner_color == 'black':
            self.black_elo += K_FACTOR * (1 - expected_score_black)
            self.white_elo += K_FACTOR * (0 - expected_score_white)
        else:
            self.white_elo += K_FACTOR * (0.5 - expected_score_white)
            self.black_elo += K_FACTOR * (0.5 - expected_score_black)

    def reset_elo(self):
        self.white_elo = 300
        self.black_elo = 300