import torch.optim
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional
from backend.chess_agent.models.base_model import BaseModel


@dataclass
class Checkpoint:
    model_name: str
    model_state_dict: Dict[str, Any]
    model_config_dict: Dict[str, Any]

    input_shape: Tuple[int, ...]
    param_num: int

    optimizer_state_dict: Optional[Dict[str, Any]] = None
    optimizer_type: Optional[str] = None

    episode: Optional[int] = None
    loss: Optional[float] = None
    elo: Optional[int] = None


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        return cls(**data)


    @classmethod
    def create(cls, model: BaseModel, optimizer: Optional[torch.optim.Optimizer] = None,
               episode: Optional[int] = None, loss: Optional[float] = None, elo: Optional[int] = None) -> 'Checkpoint':
         optimizer_state_dict = None
         optimizer_type = None

         if optimizer is not None:
             optimizer_state_dict = optimizer.state_dict()
             optimizer_type = optimizer.__class__.__name__

         return cls(
            model_name=model.model_name,
            model_state_dict=model.state_dict(),
            model_config_dict=model.get_config().to_dict(),
            input_shape=model.input_shape,
            param_num=model.get_num_parameters(),
            optimizer_state_dict=optimizer_state_dict,
            optimizer_type=optimizer_type,
            episode=episode,
            loss=loss,
            elo=elo,
        )


    def has_optimizer(self) -> bool:
        return self.optimizer_state_dict is not None

    def is_training_checkpoint(self) -> bool:
        return self.episode is not None or self.loss is not None