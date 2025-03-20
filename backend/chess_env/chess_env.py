import chess
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class ChessEnv(gym.Env):

    def __init__(self):
        super(ChessEnv, self).__init__()
        self.board = chess.Board()
        self.action_space = spaces.Discrete(4672) # all possible moves for each piece
        self.observation_space = spaces.Box(0, 1, shape=(8, 8, 12), dtype=np.float32) # 12 = all white pieces [0:6] and black pieces [6:12]

    def reset(self, seed=None, options=None):
        self.board.reset()
        return self.get_observation(board=self.board), {} # we should also return info dict but for now its empty


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
            row, col = divmod(square, 8) # getting the coordinate from the square number e.g.: we have square no. 10 so we have  10 // 8 and 10 % 8  = (1, 2) =  B3
            piece_type = piece_map[piece.piece_type]

            if piece.color == chess.WHITE:
                observation[row, col, piece_type] = 1
            else:
                observation[row, col, piece_type + 6] = 1

        return observation