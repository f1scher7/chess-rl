import torch
import numpy as np
from backend.chess_agent.agent_config import *
from backend.utils.chess_env_utils import ChessEnvUtils
from backend.utils.utils import Utils


class SelfPlay:

    def __init__(self):
        self.all_white_log_probs = []
        self.all_black_log_probs = []
        self.all_white_rewards = []
        self.all_black_rewards = []


    def train(self, env, model, optimizer, model_save=True):
        for episode in range (1, EPISODES + 1):
            self.collect_episode(env=env, model=model)

            if episode % UPDATE_FREQUENCY == 0:
                self.compute_discounted_rewards()
                loss = self.update_model(optimizer=optimizer)
                self.reset_probs_and_rewards()

                print("Model was updated!")
                self.log_training_info(episode=episode, loss=loss)
                env.save_game_pgn(episode=episode)

        if model_save:
            Utils.save_model(model=model, optimizer=optimizer)


    def update_model(self, optimizer):
        optimizer.zero_grad()
        loss = self.compute_loss()
        loss.backward() # gradients calculation
        optimizer.step() # weights and biases update

        return loss


    def compute_loss(self):
        white_loss = -torch.sum(torch.tensor(data=self.all_white_log_probs, dtype=torch.float32) * torch.tensor(data=self.all_white_rewards, dtype=torch.float32))
        black_loss = -torch.sum(torch.tensor(data=self.all_black_log_probs, dtype=torch.float32) * torch.tensor(data=self.all_black_rewards, dtype=torch.float32))

        return white_loss + black_loss


    def collect_episode(self, env, model):
        observation, info = env.reset()
        white_reward = 0
        black_reward = 0
        done = False

        while not done:
            state = observation

            observation, white_reward, black_reward, done, info, log_prob = SelfPlay.make_step(env=env, model=model, observation=observation)

            if env.board.turn:
                self.all_white_rewards.append((state, white_reward))
                self.all_white_log_probs.append(log_prob)
            else:
                self.all_black_rewards.append((state, black_reward))
                self.all_black_log_probs.append(log_prob)

        self.all_white_rewards.append((observation, white_reward))
        self.all_black_rewards.append((observation, black_reward))


    def compute_discounted_rewards(self):
        white_cumulative_rewards = 0
        black_cumulative_rewards = 0

        white_discounted_rewards = []
        black_discounted_rewards = []

        for _, reward in reversed(self.all_white_rewards):
            white_cumulative_rewards = reward + GAMMA * white_cumulative_rewards
            white_discounted_rewards.insert(0, white_cumulative_rewards)

        for _, reward in reversed(self.all_black_rewards):
            black_cumulative_rewards = reward + GAMMA * black_cumulative_rewards
            black_discounted_rewards.insert(0, black_cumulative_rewards)

        self.all_white_rewards = torch.tensor(data=white_discounted_rewards, dtype=torch.float32)
        self.all_black_rewards = torch.tensor(data=black_discounted_rewards, dtype=torch.float32)


    @staticmethod
    def make_step(env, model, observation):
        # observation_tensor = (batch_size = 1, channels, height, width)
        observation_tensor = torch.tensor(data=observation, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)

        probabilities = model(observation_tensor)
        probabilities_np = probabilities.detach().numpy()[0]

        legal_actions_idx = ChessEnvUtils.get_legal_actions_idx(env.board)

        mask = np.zeros(probabilities_np.shape)
        mask[legal_actions_idx] = 1
        masked_probs = mask * probabilities_np
        masked_probs_norm = masked_probs / masked_probs.sum()

        if np.random.rand() < EPSILON or masked_probs.sum() == 0:
            action_chosen = np.random.choice(legal_actions_idx)
        else:
            action_chosen = np.random.choice(len(masked_probs_norm), p=masked_probs_norm)

        log_prob = torch.log(input=torch.tensor(masked_probs_norm[action_chosen] + 1e-8, dtype=torch.float32))

        observation, (white_reward, black_reward), done, info = env.step(action_chosen)

        return observation, white_reward, black_reward, done, info, log_prob


    def reset_probs_and_rewards(self):
        self.all_white_log_probs = []
        self.all_black_log_probs = []
        self.all_white_rewards = []
        self.all_black_rewards = []


    def log_training_info(self, episode, loss):
        print(f"Episode: {episode}")
        print(f"Loss: {loss:.5f}")

        if self.all_white_rewards and self.all_black_rewards:
            avg_white_rewards = sum(self.all_white_rewards) / len(self.all_white_rewards)
            avg_black_rewards = sum(self.all_black_rewards) / len(self.all_black_rewards)

            print(f"Avg white rewards: {avg_white_rewards:.5f}")
            print(f"Avg black rewards: {avg_black_rewards:.5f}")

        print("=" * 40)