import os
from dotenv import load_dotenv


load_dotenv()


class PathConfig:
    SAVED_MODELS_PATH_BASE: str = os.getenv("SAVED_MODELS_PATH")
    SAVED_GAMES_PATH_BASE: str = os.getenv("SAVED_GAMES_PATH")
    SAVED_GRAPHS_PATH_BASE: str = os.getenv("SAVED_GRAPHS_PATH")