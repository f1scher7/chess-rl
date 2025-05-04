from enum import Enum
from pydantic import BaseModel
from typing import List


class File(BaseModel):
    file_name: str


class FileList(BaseModel):
    file_names: List[str]


class PathType(str, Enum):
    games = "games"
    models = "models"


class SavedGameContent(BaseModel):
    white_elo: int
    black_elo: int
    result: str
    moves: list


class Move(BaseModel):
    move: str
