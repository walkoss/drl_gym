import numpy as np

from tensorflow.python.keras import Sequential
from tensorflow.python.keras.activations import linear, tanh
from tensorflow.python.keras.layers import Dense, Conv2D, Flatten
from tensorflow.python.keras.losses import mse
from tensorflow.python.keras.optimizers import SGD, Adam
from tensorflow.python.keras.models import load_model


class DQNBrain:
    def __init__(
        self,
        output_dim: int,
        learning_rate: float = 0.0001,
        hidden_layers_count: int = 0,
        neurons_per_hidden_layer: int = 0,
        activation: str = "tanh",
        using_convolution: bool = False,
    ):
        self.model = Sequential()

        if using_convolution:
            self.model.add(Conv2D(64, kernel_size=3, activation=activation))
            self.model.add(Conv2D(32, kernel_size=3, activation=activation))
            self.model.add(Flatten())
            self.model.add(Dense(neurons_per_hidden_layer, activation=activation))
        else:
            for _ in range(hidden_layers_count):
                self.model.add(Dense(neurons_per_hidden_layer, activation=activation))

        self.model.add(Dense(output_dim, activation=linear, use_bias=False))
        self.model.compile(loss=mse, optimizer=Adam(lr=learning_rate))

    def predict(self, state: np.ndarray) -> np.ndarray:
        return self.model.predict(np.array((state,)))[0]

    def train(self, state: np.ndarray, chosen_action_mask: np.ndarray, target: float):
        target_vec = chosen_action_mask * target + (
            1 - chosen_action_mask
        ) * self.predict(state)
        self.model.train_on_batch(np.array((state,)), np.array((target_vec,)))

    def save_model(self, filename: str):
        self.model.save(f"{filename}.h5")

    def load_model(self, filename: str):
        self.model = load_model(filename)
