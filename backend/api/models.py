from enum import Enum
from pydantic import BaseModel
from typing import List
from cachetools import LRUCache
from backend.utils.utils import Utils


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
    move_str: str


class ModelStore:
    _cache = LRUCache(maxsize=7)

    @classmethod
    def load_model(cls, model_name):
        if model_name not in cls._cache:
            model, optimizer = Utils.create_default_model_and_optimizer()
            Utils.load_model(model=model, optimizer=optimizer, file_name=model_name)
            cls._cache[model_name] = (model, optimizer)

        return cls._cache[model_name]