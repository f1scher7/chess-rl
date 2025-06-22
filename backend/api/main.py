import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.models import *
from backend.chess_agent.vs_human import VsHuman
from backend.configs.path_config import PathConfig
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
async def get_file_list(path_type: PathType) -> FileList:
    path_map = {
        PathType.games: PathConfig.SAVED_GAMES_PATH_BASE,
        PathType.models: PathConfig.SAVED_MODELS_PATH_BASE
    }

    path = path_map.get(path_type, "")

    if path:
        file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        file_names.sort(key=lambda f: os.path.getmtime(os.path.join(path, f)), reverse=True)

        file_list = FileList(file_names=file_names)

        return file_list
    else:
        return FileList(file_names=[])


@app.get("/saved-game", response_model=SavedGameContent)
async def get_saved_game(file: str) -> SavedGameContent:
    file_path = os.path.join(PathConfig.SAVED_GAMES_PATH_BASE, file)

    if os.path.isfile(file_path):
        saved_game_content = Utils.extract_data_from_pgn(file=file_path)
        return saved_game_content
    else:
        return SavedGameContent(white_elo='-1', black_elo='-1', result="", moves=[])


@app.get("/play-vs-agent", response_model=Move)
async def load_agent(model_file_name: str, fen: str) -> Move:
    model, _ = ModelStore.load_model(model_file_name)

    if model:
        fen_after_move = Move(move_str=VsHuman.make_move(model=model, fen=fen))
        return fen_after_move
    else:
        return Move(move_str="")
