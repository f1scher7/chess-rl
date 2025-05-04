import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.models import *
from backend.config import SAVED_GAMES_PATH, SAVED_MODELS_PATH
from backend.utils.utils import Utils


app = FastAPI()

origins = [
    "http://localhost:3007",
    "http://127.0.0.1:3007",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/file-list", response_model=FileList)
async def get_file_list(path_type: PathType):
    path_map = {
        PathType.games: SAVED_GAMES_PATH,
        PathType.models: SAVED_MODELS_PATH
    }

    path = path_map.get(path_type, "")

    if path:
        file_list = FileList(file_names=[
            f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
        ])
        return file_list
    else:
        return FileList(file_names=[])


@app.get("/saved-game", response_model=SavedGameContent)
async def get_saved_game(file: File):
    file_path = os.path.join(SAVED_GAMES_PATH, file.file_name)

    if os.path.isfile(file_path):
        saved_game_content = Utils.extract_data_from_pgn(file=file_path)
        return saved_game_content
    else:
        return SavedGameContent(white_elo=-1, black_elo=-1, result="", moves=[])