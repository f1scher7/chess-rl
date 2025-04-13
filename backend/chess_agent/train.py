import torch
import torch.optim as optim
import numpy as np
from backend.chess_env.chess_env import ChessEnv
from backend.chess_agent.policy import ChessPolicy
from backend.utils.chess_env_utils import ChessEnvUtils
from backend.chess_agent.agent_config import *


chess_env = ChessEnv()
chess_model = ChessPolicy(
    conv_layers_num=3,
    in_channels_list=[12, 64, 128],
    out_channels_list=[64, 128, 256],
    kernel_size_list=[3, 3, 3],
    fc_layers_num=2,
    fc_in_features_list=[16384, 1024],
    fc_out_features_list=[1024, 4762],
)

optimizer = optim.Adam(chess_model.parameters(), lr=LEARNING_RATE)



