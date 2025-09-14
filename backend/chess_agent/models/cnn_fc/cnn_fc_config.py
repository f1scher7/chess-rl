from dataclasses import dataclass
from typing import List
from backend.chess_agent.models.base_model_config import BaseModelConfig
from backend.configs.game_config import GameConfig
from backend.enums import ModelType
from backend.utils.utils import Utils


@dataclass(frozen=True)
class CnnFcConfig(BaseModelConfig):
    model_type = ModelType.CNN_FC

    conv_layer_num: int
    in_channel_lst: List[int]
    out_channel_lst: List[int]
    kernel_size_lst: List[int]
    stride: int
    padding_lst: List[int]

    fc_layer_num: int
    fc_in_feature_lst: List[int]
    fc_out_feature_lst: List[int]

    dropout_prob_conv_lst: List[float]
    dropout_prob_fc_lst: List[float]


    def __post_init__(self):
        Utils.validate_lst_length(lst=self.in_channel_lst, expected_len=self.conv_layer_num, name="in_channel_lst")
        Utils.validate_lst_length(lst=self.out_channel_lst, expected_len=self.conv_layer_num, name="out_channel_lst")
        Utils.validate_lst_length(lst=self.kernel_size_lst, expected_len=self.conv_layer_num, name="kernel_size_lst")
        Utils.validate_lst_length(lst=self.padding_lst, expected_len=self.conv_layer_num, name="padding_size_lst")
        Utils.validate_lst_length(lst=self.dropout_prob_conv_lst, expected_len=self.conv_layer_num, name="dropout_prob_conv_lst")

        Utils.validate_lst_length(lst=self.fc_in_feature_lst, expected_len=self.fc_layer_num, name="fc_in_feature_lst")
        Utils.validate_lst_length(lst=self.fc_out_feature_lst, expected_len=self.fc_layer_num, name="fc_out_feature_lst")
        Utils.validate_lst_length(lst=self.dropout_prob_fc_lst, expected_len=self.fc_layer_num, name="dropout_prob_fc_lst")

        for i in range(self.conv_layer_num):
            Utils.validate_prob(val=self.dropout_prob_conv_lst[i], name="dropout_prob_conv_lst[i]")

        for i in range(self.fc_layer_num):
            Utils.validate_prob(val=self.dropout_prob_fc_lst[i], name="dropout_prob_fc_lst[i]")

    # TODO: review the values
    @classmethod
    def for_4gb_vram(cls):
        kernel_sizes = [3, 3, 3]

        return cls(
            model_type=ModelType.CNN_FC, input_shape=(12, 8, 8),
            conv_layer_num=3, in_channel_lst=[12, 64, 128], out_channel_lst=[64, 128, 256],
            kernel_size_lst=[3, 3, 3], stride=1, padding_lst=[k // 2 for k in kernel_sizes],
            fc_layer_num=2, fc_in_feature_lst=[16384, 2048], fc_out_feature_lst=[2048, GameConfig.ACTION_SPACE], # TODO: fix ACTION_SPACE (that value has to change depends on amount of legal moves while playing)
            dropout_prob_conv_lst=[0.1, 0.1, 0.1], dropout_prob_fc_lst=[0.1, 0.1, 0.1]
        )