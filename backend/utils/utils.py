import torch
import chess.pgn
from datetime import datetime
from io import StringIO
from backend.config import SAVED_MODELS_PATH
from backend.api.models import SavedGameContent


class Utils:

    @staticmethod
    def get_device():
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @staticmethod
    def save_model(model, optimizer):
        # filename = f"chess-rl-by-f1scher7-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        filename = f"chess-rl-by-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        final_path = SAVED_MODELS_PATH + filename

        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, final_path)

        print(f"Model was saved: {final_path}")


    @staticmethod
    def load_model(model, optimizer, path):
        checkpoint = torch.load(path)

        if model and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])

        if optimizer and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        print(f"Loaded!")


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

        return SavedGameContent(white_elo=white_elo, black_elo=black_elo, result=result, moves=moves)
