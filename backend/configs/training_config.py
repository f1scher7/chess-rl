class TrainingConfig:
    INIT_EPISODE: int = 1
    EPISODES: int = 3000

    LEARNING_RATE: float = 0.0001  # For the RL default value is 0.0001

    GAMMA: float = 0.99  # Discount factor defining how much future rewards have influence on the model
                         # If gamma = 0: the model will focus on the current rewards
                         # If gamma = 0.99: the model will focus on the future rewards
    EPSILON: float = 0.2  # Exploration rate defining how often model makes random moves to explore chess board

    UPDATE_FREQUENCY: int = 2  # after n episodes model will be updated