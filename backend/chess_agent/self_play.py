import torch
import numpy as np
from torch.distributions import Categorical

from backend.chess_agent.agent_config import *
from backend.utils.chess_env_utils import ChessEnvUtils
from backend.utils.utils import Utils


class SelfPlay:

    def __init__(self, device):
        self.device = device

        self.all_white_log_probs = []
        self.all_black_log_probs = []
        self.all_white_rewards = []
        self.all_black_rewards = []


    def train(self, env, model, optimizer, model_save=True):
        interrupted = False

        try:
            for episode in range (1, EPISODES + 1):
                self.collect_episode(env=env, model=model)

                print(f"Avg eval score: {sum(env.eval_score_list) / len(env.eval_score_list)}")
                env.eval_score_list = []

                if episode % UPDATE_FREQUENCY == 0:
                    self.compute_discounted_rewards()

                    loss = self.update_model(optimizer=optimizer)

                    print("Model was updated!")
                    self.log_training_info(episode=episode, loss=loss)
                    env.save_game_pgn(episode=episode)
                    print("=" * 40)

                    self.reset_probs_and_rewards()
        except KeyboardInterrupt:
            if model_save:
                interrupted = True
                print("Training interrupted! Saving model...")
                Utils.save_model(model=model, optimizer=optimizer)
        finally:
            if model_save and not interrupted:
                Utils.save_model(model=model, optimizer=optimizer)


    def update_model(self, optimizer):
        optimizer.zero_grad()
        loss = self.compute_loss()
        loss.backward()  # gradients calculation
        optimizer.step()  # weights and biases update

        return loss


    def compute_loss(self):
        white_log_probs = torch.stack(self.all_white_log_probs)
        black_log_probs = torch.stack(self.all_black_log_probs)

        if not isinstance(self.all_white_rewards, torch.Tensor):
            self.all_white_rewards = torch.tensor(data=self.all_white_rewards, dtype=torch.float32).to(device=self.device).to(device=self.device)

        if not isinstance(self.all_black_rewards, torch.Tensor):
            self.all_white_rewards = torch.tensor(data=self.all_black_rewards, dtype=torch.float32).to(device=self.device).to(device=self.device)

        white_loss = -(white_log_probs * self.all_white_rewards).sum()
        black_loss = -(black_log_probs * self.all_black_rewards).sum()

        return white_loss + black_loss


    def collect_episode(self, env, model):
        observation, info = env.reset()
        white_reward = 0
        black_reward = 0

        white_log_prob = None
        black_log_prob = None

        done = False

        while not done:
            observation, white_reward, black_reward, done, info, log_prob = SelfPlay.make_step(env=env, model=model, observation=observation, device=self.device)

            if env.board.turn:
                self.all_white_rewards.append(white_reward)
                self.all_white_log_probs.append(log_prob)
                white_log_prob = log_prob
            else:
                self.all_black_rewards.append(black_reward)
                self.all_black_log_probs.append(log_prob)
                black_log_prob = log_prob

        if black_log_prob and white_log_prob:
            self.all_white_log_probs.append(white_log_prob)
            self.all_black_log_probs.append(black_log_prob)

        self.all_white_rewards.append(white_reward)
        self.all_black_rewards.append(black_reward)


    def compute_discounted_rewards(self):
        white_cumulative_rewards = 0
        black_cumulative_rewards = 0

        white_discounted_rewards = []
        black_discounted_rewards = []

        for reward in reversed(self.all_white_rewards):
            white_cumulative_rewards = reward + GAMMA * white_cumulative_rewards
            white_discounted_rewards.insert(0, white_cumulative_rewards)

        for reward in reversed(self.all_black_rewards):
            black_cumulative_rewards = reward + GAMMA * black_cumulative_rewards
            black_discounted_rewards.insert(0, black_cumulative_rewards)

        self.all_white_rewards = torch.tensor(data=white_discounted_rewards, dtype=torch.float32).to(device=self.device)
        self.all_black_rewards = torch.tensor(data=black_discounted_rewards, dtype=torch.float32).to(device=self.device)


    @staticmethod
    def make_step(env, model, observation, device):
        # observation_tensor = (batch_size = 1, channels, height, width)
        observation_tensor = torch.tensor(data=observation, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device=device)

        probabilities = model(observation_tensor)
        legal_actions_idx = ChessEnvUtils.get_legal_actions_idx(env.board)

        mask = torch.zeros_like(probabilities)
        mask[0, legal_actions_idx] = 1.0
        masked_probs = mask * probabilities
        masked_probs_norm = masked_probs / masked_probs.sum()

        dist = Categorical(masked_probs_norm)  # discrete distribution

        if np.random.rand() < EPSILON or masked_probs.sum() == 0:
            random_idx = torch.randint(len(legal_actions_idx), (1,)).item()
            action_chosen = legal_actions_idx[random_idx]
            action_chosen = torch.tensor(data=action_chosen, dtype=torch.long).to(device=device)
        else:
            action_chosen = dist.sample()

        log_prob = dist.log_prob(action_chosen)

        observation, (white_reward, black_reward), done, info = env.step(action_chosen.item())

        return observation, white_reward, black_reward, done, info, log_prob


    def reset_probs_and_rewards(self):
        self.all_white_log_probs = []
        self.all_black_log_probs = []
        self.all_white_rewards = []
        self.all_black_rewards = []


    def log_training_info(self, episode, loss):
        print(f"Episode: {episode}")
        print(f"Loss: {loss:.5f}")

        if isinstance(self.all_white_rewards, torch.Tensor):
            avg_white_rewards = self.all_white_rewards.mean().item()
            print(f"Avg white rewards: {avg_white_rewards:.5f}")

        if isinstance(self.all_black_rewards, torch.Tensor):
            avg_black_rewards = self.all_black_rewards.mean().item()
            print(f"Avg black rewards: {avg_black_rewards:.5f}")
