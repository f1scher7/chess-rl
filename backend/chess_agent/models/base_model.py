import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import Tuple
from backend.chess_agent.models.base_model_config import BaseModelConfig


class BaseModel(ABC, nn.Module):

    def __init__(self, input_shape: Tuple[int, ...], **kwargs):
        super().__init__()
        self.input_shape = input_shape
        self.model_name = self.__class__.__name__


    @abstractmethod
    def init_weights(self):
        pass

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def get_config(self) -> BaseModelConfig:
        pass

    def get_num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)