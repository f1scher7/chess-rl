import torch
import chess.pgn
from typing import List, Any
from io import StringIO
from pathlib import Path
from backend.api.models import SavedGameContent


class Utils:

    @staticmethod
    def get_device() -> torch.device:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @staticmethod
    def validate_lst_length(lst: List[Any], expected_len: int, name: str) -> None:
        lst_len = len(lst)
        if lst_len != expected_len:
            raise ValueError(f"{name} ({lst_len}) != expected ({expected_len})")

    @staticmethod
    def validate_prob(val: float, name: str) -> None:
        if 0.0 > val or val >= 1.0:
            raise ValueError(f"{name} ({val}) is not in range [0.0, 1.0)")


    @staticmethod
    def extract_data_from_pgn(file: str | Path) -> SavedGameContent:
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