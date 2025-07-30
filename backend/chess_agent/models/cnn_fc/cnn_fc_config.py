from dataclasses import dataclass
from typing import List, Any
from backend.chess_agent.models.base_model_config import BaseModelConfig
from backend.enums import ModelType
from backend.utils.utils import Utils


@dataclass(frozen=True)
class CnnFcConfig(BaseModelConfig):
    model_type = ModelType.CNN_FC.value

    conv_layers_num: int
    in_channel_lst: List[int]
    out_channel_lst: List[int]
    kernel_size_lst: List[int]
    stride: int
    padding: int
    dropout_prob_conv_lst: List[float]

    fc_layers_num: int
    fc_in_feature_lst: List[int]
    fc_out_feature_lst: List[int]
    dropout_prob_fc_lst: List[float]


    def __post_init__(self):
        Utils.validate_lst_length(lst=self.in_channel_lst, expected_len=self.conv_layers_num, name="in_channel_lst")
        Utils.validate_lst_length(lst=self.out_channel_lst, expected_len=self.conv_layers_num, name="out_channel_lst")
        Utils.validate_lst_length(lst=self.kernel_size_lst, expected_len=self.conv_layers_num, name="kernel_size_lst")
        Utils.validate_lst_length(lst=self.dropout_prob_conv_lst, expected_len=self.conv_layers_num, name="dropout_prob_conv_lst")

        Utils.validate_lst_length(lst=self.fc_in_feature_lst, expected_len=self.fc_layers_num, name="fc_in_feature_lst")
        Utils.validate_lst_length(lst=self.fc_out_feature_lst, expected_len=self.fc_layers_num, name="fc_out_feature_lst")
        Utils.validate_lst_length(lst=self.dropout_prob_fc_lst, expected_len=self.fc_layers_num, name="dropout_prob_fc_lst")

        for i in range(self.conv_layers_num):
            Utils.validate_prob(val=self.dropout_prob_conv_lst[i], name="dropout_prob_conv_lst[i]")

        for i in range(self.fc_layers_num):
            Utils.validate_prob(val=self.dropout_prob_fc_lst[i], name="dropout_prob_fc_lst[i]")




