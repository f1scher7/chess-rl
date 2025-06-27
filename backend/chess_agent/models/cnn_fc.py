import torch.nn as nn
import torch.nn.functional as F


class CnnPlusFc(nn.Module):

    def __init__(self, conv_layers_num, in_channels_list, out_channels_list, kernel_size_list,
                 fc_layers_num, fc_in_features_list, fc_out_features_list,
                 dropout_probability_conv=0.1, dropout_probability_fc=0.1):
        super(CnnPlusFc, self).__init__()

        self.conv_layers_num = conv_layers_num
        self.fc_layers_num = fc_layers_num
        self.dropout_probability_conv = dropout_probability_conv
        self.dropout_probability_fc = dropout_probability_fc

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

        # normalization for each channel
        self.instance_norm_layers = nn.ModuleList([
            nn.InstanceNorm2d(
                num_features=out_channels_list[i],
                affine=True  # instance_norm_layer's weights and biases (learning scaling and shifting)
            ) for i in range(self.conv_layers_num)
        ])

        self.fc_layers = nn.ModuleList([
            nn.Linear(
                in_features=fc_in_features_list[i],
                out_features=fc_out_features_list[i]
            )
            for i in range(fc_layers_num)
        ])

        self.layer_norm = nn.LayerNorm(normalized_shape=fc_in_features_list[0])

        self.__initialize_weights()


    def __initialize_weights(self):
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


    def forward(self, x):
        for i, conv_layer in enumerate(self.conv_layers):
            x = conv_layer(x)
            x = self.instance_norm_layers[i](x)
            x = F.relu(x)
            x = F.dropout2d(input=x, p=self.dropout_probability_conv, training=self.training)

        x = x.view(x.size(0), -1)
        x = self.layer_norm(x)

        for i, fc_layer in enumerate(self.fc_layers[:-1]):
            x = F.relu(fc_layer(x))
            x = F.dropout(input=x, p=self.dropout_probability_fc, training=self.training)

        # Last FC layer
        x = self.fc_layers[-1](x)

        return x
