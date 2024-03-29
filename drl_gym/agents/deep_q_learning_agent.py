from tensorflow.python.keras.metrics import *
from tensorflow.python.keras.utils import *
from tensorflow.python.keras.models import load_model

from drl_gym.brains import DQNBrain
from drl_gym.contracts import Agent, GameState


# si gs1 == gs2 => hash(gs1) == hash(gs2)
# si gs1 != gs2 => hash(gs1) != hash(gs2) || hash(gs1) == hash(gs2)


class DeepQLearningAgent(Agent):
    def __init__(
        self,
        action_space_size: int,
        alpha: float = 0.01,
        gamma: float = 0.999,
        epsilon: float = 0.1,
        hidden_layers_count: int = 5,
        neurons_per_hidden_layer: int = 128,
        activation: str = "tanh",
        using_convolution: bool = False,
    ):
        self.Q = DQNBrain(
            output_dim=action_space_size,
            learning_rate=alpha,
            hidden_layers_count=hidden_layers_count,
            neurons_per_hidden_layer=neurons_per_hidden_layer,
            activation=activation,
            using_convolution=using_convolution,
        )
        self.using_convolution = using_convolution
        self.action_space_size = action_space_size
        self.s = None
        self.a = None
        self.r = None
        self.gamma = gamma
        self.epsilon = epsilon

    def act(self, gs: GameState) -> int:
        available_actions = gs.get_available_actions(gs.get_active_player())

        state_vec = gs.get_vectorized_state(
            mode="2D" if self.using_convolution else None
        )
        predicted_Q_values = self.Q.predict(state_vec)

        if np.random.random() <= self.epsilon:
            chosen_action = np.random.choice(available_actions)
        else:
            chosen_action = available_actions[
                int(np.argmax(predicted_Q_values[available_actions]))
            ]

        if self.s is not None:
            target = self.r + self.gamma * max(predicted_Q_values[available_actions])
            self.Q.train(self.s, self.a, target)

        self.s = state_vec
        self.a = to_categorical(chosen_action, self.action_space_size)
        self.r = 0.0

        return chosen_action

    def observe(self, r: float, t: bool, player_index: int):
        if self.r is None:
            return

        self.r += r

        if t:
            target = self.r
            self.Q.train(self.s, self.a, target)
            self.s = None
            self.a = None
            self.r = None

    def save_model(self, filename: str):
        self.Q.save_model(filename)

    def load_model(self, filename: str):
        self.Q.load_model(filename)
