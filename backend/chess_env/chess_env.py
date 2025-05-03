import os
import chess
import chess.pgn
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from backend.chess_env.eval import Eval
from backend.config import WHITE_ELO, BLACK_ELO, TERMINAL_BONUS, SAVED_GAMES_PATH
from backend.utils.chess_env_utils import ChessEnvUtils


class ChessEnv(gym.Env):

    def __init__(self):
        super(ChessEnv, self).__init__()

        self.board = chess.Board()
        self.white_elo = WHITE_ELO
        self.black_elo = BLACK_ELO

        self.action_space = spaces.Discrete(4672)  # all possible moves for each piece
        self.observation_space = spaces.Box(0, 1, shape=(8, 8, 12), dtype=np.float32)  # 12 = all white pieces [0:6] and black pieces [6:12]

        self.eval_score_list = []


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
                white_reward, black_reward = TERMINAL_BONUS, -TERMINAL_BONUS
            else:
                white_reward, black_reward = -TERMINAL_BONUS, TERMINAL_BONUS

            self.white_elo, self.black_elo = ChessEnvUtils.update_elo(winner_color=winner_color, white_elo=self.white_elo, black_elo=self.black_elo)

            return white_reward, black_reward, True

        elif self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.can_claim_threefold_repetition() or self.board.is_fivefold_repetition():
            self.white_elo, self.black_elo = ChessEnvUtils.update_elo(winner_color='draw', white_elo=self.white_elo, black_elo=self.black_elo)
            return 0, 0, True

        eval_score = Eval.evaluate_board(self.board)

        if self.board.turn == chess.WHITE:
            white_reward = eval_score
            black_reward = -eval_score
        else:
            white_reward = -eval_score
            black_reward = eval_score

        self.eval_score_list.append(eval_score)

        return white_reward, black_reward, False



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
            row, col = divmod(square, 8)  # getting the coordinate from the square number e.g.: we have square no. 10 so we have  10 // 8 and 10 % 8  = (1, 2) =  B3
            piece_type = piece_map[piece.piece_type]

            if piece.color == chess.WHITE:
                observation[row, col, piece_type] = 1
            else:
                observation[row, col, piece_type + 6] = 1

        return observation


    def decode_action(self, action_no):
        # Decode the number of action to legal chess move e.g. e4, because AI choose only the number of action
        for move in self.board.legal_moves:
            if ChessEnvUtils.get_move_idx(move=move) == action_no:
                return move

        return None


    def reset(self, seed=None, options=None):
        self.board.reset()
        return self.get_observation(board=self.board), {}  # we should also return info dict but for now its empty :D


    def reset_elo(self):
        self.white_elo = 300
        self.black_elo = 300


    def save_game_pgn(self, episode, event_name="Self-play", mode_name="self-play-train"):
        game = chess.pgn.Game.from_board(board=self.board)
        game.headers["Event"] = event_name
        game.headers["White"] = f"elo: {self.white_elo}"
        game.headers["Black"] = f"elo: {self.black_elo}"
        game.headers["Result"] = self.board.result()

        pgn_str = str(game)

        file_name = f"{mode_name}-episode{episode}-w_elo{int(self.white_elo)}-b_elo{int(self.black_elo)}.pgn"
        file_path = os.path.join(SAVED_GAMES_PATH, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(pgn_str)

        print(f"Game was saved to: {file_path}")
