import chess
import torch
from torch.distributions import Categorical
from backend.chess_agent.models.cnn_fc.cnn_fc import CnnFc
from backend.chess_env.chess_env import ChessEnv
from backend.utils.utils import Utils
from backend.utils.chess_env_utils import ChessEnvUtils


class VsHuman:

    @staticmethod
    def make_move(model: CnnFc, fen: str):
        board = chess.Board(fen)
        observation = ChessEnv.get_observation(board)

        observation_tensor = torch.tensor(data=observation, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device=Utils.get_device())

        logits = model(observation_tensor)
        legal_action_idxs = ChessEnvUtils.get_legal_action_idxs(board)

        mask = torch.full_like(input=logits, fill_value=float('-inf'))
        mask[0, legal_action_idxs] = 0.0
        masked_logits = mask + logits

        probs = torch.softmax(input=masked_logits, dim=1)

        dist = Categorical(probs)  # discrete distribution
        action_chosen = dist.sample()

        move = ChessEnv.decode_action(board=board, action_no=action_chosen)
        board.push(move)

        return move.uci()