import torch.optim as optim

from backend.chess_agent.agent_config import LEARNING_RATE
from backend.chess_agent.policy import ChessPolicy
from backend.chess_agent.self_play import SelfPlay
from backend.chess_env.chess_env import ChessEnv


# SELF PLAY
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

adam = optim.Adam(chess_model.parameters(), lr=LEARNING_RATE)


self_play = SelfPlay()
self_play.train(env=chess_env, model=chess_model, optimizer=adam)


