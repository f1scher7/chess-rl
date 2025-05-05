from enum import Enum
from pydantic import BaseModel
from typing import List


class ChessRlFile(BaseModel):
    file_name: str


class FileList(BaseModel):
    file_names: List[str]


class PathType(str, Enum):
    games = "games"
    models = "models"


class SavedGameContent(BaseModel):
    white_elo: str
    black_elo: str
    result: str
    moves: List[str]


class Move(BaseModel):
    move: str
