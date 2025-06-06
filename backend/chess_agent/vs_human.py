import chess
import torch
from torch.distributions import Categorical
from backend.chess_agent.policy import ChessPolicy
from backend.chess_env.chess_env import ChessEnv
from backend.utils.utils import Utils
from backend.utils.chess_env_utils import ChessEnvUtils


class VsHuman:

    @staticmethod
    def make_move(model: ChessPolicy, fen: str):
        board = chess.Board(fen)
        observation = ChessEnv.get_observation(board)

        observation_tensor = torch.tensor(data=observation, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device=Utils.get_device())

        probabilities = model(observation_tensor)
        legal_action_idxs = ChessEnvUtils.get_legal_action_idxs(board)

        mask = torch.zeros_like(probabilities)
        mask[0, legal_action_idxs] = 1.0
        masked_probs = mask * probabilities
        masked_probs_norm = masked_probs / masked_probs.sum()

        dist = Categorical(masked_probs_norm)  # discrete distribution
        action_chosen = dist.sample()

        move = ChessEnv.decode_action(board=board, action_no=action_chosen)
        board.push(move)

        return move.uci()