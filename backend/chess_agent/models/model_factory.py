from typing import Dict, Type, List
from backend.chess_agent.models.base_model import BaseModel
from backend.chess_agent.models.base_model_config import BaseModelConfig
from backend.chess_agent.models.cnn_fc.cnn_fc import CnnFc
from backend.chess_agent.models.cnn_fc.cnn_fc_config import CnnFcConfig
from backend.enums import ModelType


class ModelFactory:
    _model_registry: Dict[ModelType, Type[BaseModel]] = {
        ModelType.CNN_FC: CnnFc,
    }

    _config_registry: Dict[ModelType, Type[BaseModelConfig]] = {
        ModelType.CNN_FC: CnnFcConfig,
    }


    @classmethod
    def create_model(cls, config: BaseModelConfig, **kwargs) -> BaseModel:
        model_type = config.model_type

        if model_type not in cls._model_registry:
            raise ValueError(
                f"Unsupported model type: {model_type.value}."
                f"Available types: {cls.get_supported_model_types()}"
            )

        model_class = cls._model_registry[model_type]

        return model_class(config=config, **kwargs)

    @classmethod
    def register_model(cls, model_type: ModelType, model_class: Type[BaseModel], config_class: Type[BaseModelConfig]):
        cls._model_registry[model_type] = model_class
        cls._config_registry[model_type] = config_class

    @classmethod
    def get_supported_model_types(cls) -> List[ModelType]:
        return list(cls._model_registry.keys())

