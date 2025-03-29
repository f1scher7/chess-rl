import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class ChessPolicy(nn.Module):

    def __init__(self, conv_layers_num, in_channels_list, out_channels_list, kernel_size_list,
                 fc_layers_num, fc_in_features_list, fc_out_features_list, dropout_probability=0.5, actions_num=4672):
        super(ChessPolicy, self).__init__()

        self.conv_layers_num = conv_layers_num
        self.fc_layers_num = fc_layers_num
        self.dropout_probability = dropout_probability
        self.actions_num = actions_num

        self.conv_layers = nn.ModuleList([
            nn.Conv2d(
                in_channels=in_channels_list[i],
                out_channels=out_channels_list[i],
                kernel_size=kernel_size_list[i],
                padding=kernel_size_list[i] // 2,
                stride=1
            )
            for i in range(conv_layers_num)
        ])

        self.fc_layers = nn.ModuleList([
            nn.Linear(
                in_features=fc_in_features_list[i],
                out_features=fc_out_features_list[i]
            )
            for i in range(fc_layers_num)
        ])

        self.__initialize_weights()


    def __initialize_weights(self):
        for conv_layer in self.conv_layers:
            nn.init.kaiming_uniform_(conv_layer.weight, nonlinearity='relu')

            if conv_layer.bias is not None:
                nn.init.zeros_(conv_layer.bias)

        for fc_layer in self.fc_layers:
            nn.init.kaiming_uniform_(fc_layer.weight, nonlinearity='relu')

            if fc_layer.bias is not None:
                nn.init.zeros_(fc_layer.bias)


    def forward(self, x):
        for conv_layer in self.conv_layers:
            x = F.relu(conv_layer(x))

        x = x.view(x.size(0), -1)

        for fc_layer in self.fc_layers:
            x = F.relu(fc_layer(x))
            x = F.dropout(input=x, p=self.dropout_probability, training=self.training)

        x = F.softmax(x, dim=-1)

        return x