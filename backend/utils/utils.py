import os
import torch
import torch.optim as optim
import chess.pgn
import matplotlib.pyplot as plt
from datetime import datetime
from io import StringIO
from backend.chess_agent.agent_config import UPDATE_FREQUENCY, EPISODES, LEARNING_RATE
from backend.chess_agent.policy import ChessPolicy
from backend.config import SAVED_MODELS_PATH


class Utils:

    @staticmethod
    def get_device():
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @staticmethod
    def save_model(model, optimizer):
        # filename = f"chess-rl-by-f1scher7-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        filename = f"chess-rl-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        final_path = SAVED_MODELS_PATH + filename

        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, final_path)

        print(f"Model was saved: {final_path}")


    @staticmethod
    def load_model(model, optimizer, file_name):
        path = os.path.join(SAVED_MODELS_PATH, file_name)

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
    def plot_loss(loss_list):
        episode_list = [i for i in range(UPDATE_FREQUENCY, EPISODES + 1, UPDATE_FREQUENCY)]

        plt.plot(episode_list, loss_list, label="Loss")
        plt.title("Training Loss")
        plt.xlabel("Episodes")
        plt.ylabel("Loss")
        plt.legend()
        plt.show()