import json
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Any
from backend.enums import ModelType


@dataclass(frozen=True)
class BaseModelConfig:
    input_shape: Tuple[int, ...]
    model_type: ModelType


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data) # unpack data dict to create and return an object