import os
import torch
import torch.optim as optim
import chess.pgn
import matplotlib.pyplot as plt
from datetime import datetime
from io import StringIO
from backend.chess_agent.policy import ChessPolicy
from backend.chess_agent.agent_config import UPDATE_FREQUENCY, EPISODES, LEARNING_RATE, GAMMA, EPSILON, INIT_EPISODE
from backend.config import SAVED_MODELS_PATH, SAVED_GRAPHS_PATH, TERMINAL_BONUS, CASTLING_BONUS, EVAL_SCALING_FACTOR


class Utils:

    @staticmethod
    def get_device():
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @staticmethod
    def save_model(model, optimizer, episodes):
        filename = f"chess-rl-by-f1scher7-model-episodes{episodes}-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        final_path = os.path.join(SAVED_MODELS_PATH, filename)

        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, final_path)

        print(f"Model was saved to: {final_path}")


    @staticmethod
    def load_model(model, optimizer, file_name):
        path = str(os.path.join(SAVED_MODELS_PATH, file_name))
        checkpoint = torch.load(path)

        if model and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])

        if optimizer and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        print(f"Model and optimizer were loaded!")


    @staticmethod
    def create_default_model_and_optimizer():
        device = Utils.get_device()

        default_model = ChessPolicy(
            conv_layers_num=3,
            in_channels_list=[12, 64, 128],
            out_channels_list=[64, 128, 256],
            kernel_size_list=[3, 3, 3],
            fc_layers_num=2,
            fc_in_features_list=[16384, 2048],
            fc_out_features_list=[2048, 4762],
        ).to(device=device)

        default_optimizer = optim.Adam(default_model.parameters(), lr=LEARNING_RATE)

        return default_model, default_optimizer


    @staticmethod
    def extract_data_from_pgn(file):
        with open(file, 'r') as f:
            pgn_text = f.read()

        pgn_io = StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)

        white_elo = game.headers["white_elo"].split('.')[0]
        black_elo = game.headers["black_elo"].split('.')[0]
        result = game.headers["result"]

        moves = []

        for move in game.mainline_moves():
            moves.append(move.uci())

        from backend.api.models import SavedGameContent
        return SavedGameContent(white_elo=white_elo, black_elo=black_elo, result=result, moves=moves)


    @staticmethod
    def plot_loss(loss_list, mode):
        episodes = EPISODES if EPISODES % 2 == 0 else EPISODES - 1
        episode_list = [i for i in range(INIT_EPISODE - 1, episodes, UPDATE_FREQUENCY)]

        main_title = "Training Loss"
        training_params = f"Training: Episodes={EPISODES} • LR={LEARNING_RATE} • γ={GAMMA}"
        exploration_params = f"Exploration: ε={EPSILON} • Update Freq={UPDATE_FREQUENCY}"
        reward_params = f"Rewards: Terminal={TERMINAL_BONUS} • Castling={CASTLING_BONUS} • Eval Scale={EVAL_SCALING_FACTOR}"

        file_name = f"{mode}_loss-graph_{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}"
        final_path = os.path.join(SAVED_GRAPHS_PATH, file_name)

        plt.figure(figsize=(14, 10))
        plt.plot(episode_list, loss_list, label="Loss", linewidth=2)

        plt.suptitle(main_title, fontsize=16, fontweight='bold', y=0.95)
        plt.figtext(0.5, 0.90, training_params, ha='center', fontsize=11, style='italic')
        plt.figtext(0.5, 0.87, exploration_params, ha='center', fontsize=11, style='italic')
        plt.figtext(0.5, 0.84, reward_params, ha='center', fontsize=11, style='italic')

        plt.xlabel("Episodes", fontsize=12)
        plt.ylabel("Loss", fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.subplots_adjust(top=0.80)

        plt.savefig(final_path, dpi=300, bbox_inches='tight')
        print(f"Loss graph was saved to: {final_path}")

        plt.show()