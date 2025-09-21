import torch
import torch.nn as nn
import torch.nn.functional as F
from backend.chess_agent.models.base_model import BaseModel
from backend.chess_agent.models.base_model_config import BaseModelConfig
from backend.chess_agent.models.cnn_fc.cnn_fc_config import CnnFcConfig


class CnnFc(BaseModel):

    def __init__(self, config: CnnFcConfig, **kwargs):
        super().__init__(config.input_shape, **kwargs)

        self.config = config

        self.conv_layers = nn.ModuleList([
            nn.Conv2d(
                in_channels=config.in_channel_lst[i],
                out_channels=config.out_channel_lst[i],
                kernel_size=config.kernel_size_lst[i],
                padding=config.padding_lst[i] // 2,
                stride=config.stride
            )
            for i in range(config.conv_layer_num)
        ])

        # normalization for each channel
        self.instance_norm_layers = nn.ModuleList([
            nn.InstanceNorm2d(
                num_features=config.out_channel_lst[i],
                affine=True  # instance_norm_layer's weights and biases (learning scaling and shifting)
            ) for i in range(config.conv_layer_num)
        ])

        self.fc_layers = nn.ModuleList([
            nn.Linear(
                in_features=config.fc_in_feature_lst[i],
                out_features=config.fc_out_feature_lst[i]
            )
            for i in range(config.fc_layer_num)
        ])

        self.layer_norm = nn.LayerNorm(normalized_shape=config.fc_in_feature_lst[0])

        self.init_weights()


    def init_weights(self):
        for conv_layer in self.conv_layers:
            nn.init.kaiming_uniform_(tensor=conv_layer.weight, nonlinearity='relu')  # he

            if conv_layer.bias is not None:
                nn.init.zeros_(conv_layer.bias)

        for i, fc_layer in enumerate(self.fc_layers):
            if i == len(self.fc_layers) - 1:
                nn.init.orthogonal_(tensor=fc_layer.weight, gain=0.01)
                nn.init.zeros_(fc_layer.bias)
            else:
                nn.init.kaiming_uniform_(tensor=fc_layer.weight, nonlinearity='relu')  # he

                if fc_layer.bias is not None:
                    nn.init.zeros_(fc_layer.bias)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for i, conv_layer in enumerate(self.conv_layers):
            x = conv_layer(x)
            x = self.instance_norm_layers[i](x)
            x = F.relu(x)
            x = F.dropout2d(input=x, p=self.config.dropout_prob_conv_lst[i], training=self.training)

        # flatten for FC layer
        x = x.view(x.size(0), -1)
        x = self.layer_norm(x)

        for i, fc_layer in enumerate(self.fc_layers[:-1]):
            x = F.relu(fc_layer(x))
            x = F.dropout(input=x, p=self.config.dropout_prob_fc_lst[i], training=self.training)

        # Last FC layer
        x = self.fc_layers[-1](x)

        return x


    def get_model_config(self) -> BaseModelConfig:
        return self.config