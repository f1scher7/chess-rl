import torch
import torch.optim as optim
import numpy as np
from backend.chess_env.chess_env import ChessEnv
from backend.chess_agent.policy import ChessPolicy
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


def play_episode(env, model):
    observation, info = env.reset()
    done = False
    total_reward = 0

    while not done:
        observation, white_reward, black_reward, done_temp, info = make_step(env=env, observation=observation)


def make_step(env, observation):
    # (batch_size(1), channels, height, weight)
    observation_tensor = torch.tensor(observation, dtype=torch.float32).permute(3, 0, 1).unsqueeze(0)

    probabilities_np = chess_model(x=observation_tensor).detach().numpy()[0]

    legal_actions_idx = env.get_legal_actions_idx()

    mask = np.zeros(probabilities_np)
    mask[legal_actions_idx] = 1

    masked_logits = probabilities_np * mask

    if sum(masked_logits) == 0:
        action_chosen = np.random.choice(legal_actions_idx)
    else:
        action_chosen = np.random.choice(len(probabilities_np), p=probabilities_np)

    return env.step(action_chosen)


