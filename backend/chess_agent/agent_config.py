EPISODES = 10000 # Number of chess games to play
BATCH_SIZE = 32
LEARNING_RATE = 0.0001 # For the RL default value is 0.0001

GAMMA = 0.99 # Discount factor defining how much future rewards have influence on the model
             # If gamma = 0: the model will focus on the current rewards
             # If gamma = 0.99: the model will focus on the future rewards

EPSILON = 0.2 # Exploration rate defining how often model makes random moves to explore chess board
UPDATE_FREQUENCY = 10 # after 10 games model will be updated
