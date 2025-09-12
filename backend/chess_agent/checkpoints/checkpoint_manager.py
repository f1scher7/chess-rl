import datetime
import torch.optim
from pathlib import Path
from typing import Optional
from backend.chess_agent.checkpoints.checkpoint import Checkpoint
from backend.chess_agent.models.base_model import BaseModel
from backend.configs.path_config import PathConfig
from backend.utils.utils import Utils


class CheckpointManager:

    @staticmethod
    def save_checkpoint(model: BaseModel, optimizer: Optional[torch.optim.Optimizer] = None,
                        episode: Optional[int] = None, loss: Optional[float] = None, elo: Optional[int] = None) -> str:
        is_episode = episode is not None

        checkpoint_dir = Path(f"{PathConfig.SAVED_GAMES_PATH_BASE}/{model.model_name}/checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%H-%M-%S_%d-%m-%Y')
        episode_str = f"episode{episode}" if is_episode else "episode-none"
        filename = f"{model.model_name}-checkpoint-{episode_str}-{timestamp}.pth"
        filepath = checkpoint_dir / filename

        checkpoint = Checkpoint.create(
            model=model,
            optimizer=optimizer,
            episode=episode,
            loss=loss,
            elo=elo,
        )

        torch.save(checkpoint.to_dict(), filepath)

        print(f"Checkpoint saved to {filepath}")

        return str(filepath)


    @staticmethod
    def load_checkpoint(filepath: str, model: BaseModel, optimizer: Optional[torch.optim.Optimizer] = None) -> Checkpoint:
        device = Utils.get_device()

        checkpoint_data = torch.load(filepath, map_location=device)
        checkpoint = Checkpoint.from_dict(checkpoint_data)

        model.load_state_dict(checkpoint.model_state_dict)
        print(f"Model [{model.model_name}] loaded from {filepath}")

        if optimizer is not None:
            if checkpoint.has_optimizer():
                optimizer.load_state_dict(checkpoint.optimizer_state_dict)
                print(f"Optimizer [{optimizer.__class__.__name__}] loaded from {filepath}")
            else:
                print("Warning: Optimizer requested but not found in checkpoint")

        if checkpoint.episode is not None:
            print(f"Loaded from episode: {checkpoint.episode}")
        if checkpoint.loss is not None:
            print(f"Checkpoint loss: {checkpoint.loss:.6f}")

        return checkpoint