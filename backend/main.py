from backend.chess_agent.agent_config import LEARNING_RATE
from backend.chess_agent.models.policy import CnnPlusFc
from backend.chess_agent.self_play import SelfPlay
from backend.chess_env.chess_env import ChessEnv
from backend.config import SAVED_MODELS_PATH, ACTION_SPACE
from backend.utils.utils import Utils


device = Utils.get_device()


# SELF PLAY
chess_env = ChessEnv()

# chess_model = CnnFc(
#     conv_layers_num=4,
#     in_channels_list=[12, 64, 128, 256],
#     out_channels_list=[64, 128, 256, 512],
#     kernel_size_list=[3, 3, 3, 3],
#     fc_layers_num=3,
#     fc_in_features_list=[65536, 32768, 16384],
#     fc_out_features_list=[32768, 16384, ACTION_SPACE],
# ).to(device=device)

# chess_model = CnnFc(
#     conv_layers_num=3,
#     in_channels_list=[12, 64, 128],
#     out_channels_list=[64, 128, 256],
#     kernel_size_list=[3, 3, 3],
#     fc_layers_num=3,
#     fc_in_features_list=[16384, 8192, 4096],
#     fc_out_features_list=[8192, 4096, ACTION_SPACE],
# ).to(device=device)

# FOR 4GB VRAM
chess_model = CnnPlusFc(
    conv_layers_num=3,
    in_channels_list=[12, 64, 128],
    out_channels_list=[64, 128, 256],
    kernel_size_list=[3, 3, 3],
    fc_layers_num=2,
    fc_in_features_list=[16384, 2048],
    fc_out_features_list=[2048, ACTION_SPACE],
).to(device=device)


model, optimizer = Utils.create_default_model_and_optimizer()

# LOAD MODEL AND OPTIM FROM .pth
# model_file_name = 'chess-rl-model-episodes6000-22-49-34_21-05-2025.pth'
# Utils.load_model(model=model, optimizer=optimizer, file_name=model_file_name)


self_play = SelfPlay(device=device)
self_play.train(env=chess_env, model=model, optimizer=optimizer)


