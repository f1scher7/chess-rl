import chess
import torch
import numpy as np
from torch.distributions import Categorical
from backend.chess_env.chess_env import ChessEnv
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
        self.loss_list = []

        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0

        self.save_game = False


    def train(self, env, model, optimizer, model_save=True):
        curr_episode = 0
        interrupted = False

        try:
            for episode in range (INIT_EPISODE, EPISODES + 1):
                curr_episode = episode

                self.collect_episode(env=env, model=model)
                self.log_training_info(episode=episode, eval_score_list=env.eval_score_list, loss=None)

                if episode % UPDATE_FREQUENCY == 0:
                    self.compute_discounted_rewards()

                    loss = self.update_model(model=model, optimizer=optimizer)

                    print("Model was updated!")
                    self.log_training_info(episode=episode, eval_score_list=None, loss=loss)
                    print("=" * 50)

                    self.reset_probs_and_rewards()

                if self.save_game:
                    env.save_game_pgn(episode=episode)

        except KeyboardInterrupt:
            if model_save:
                interrupted = True
                print("Training interrupted! Saving model...")
                Utils.save_model(model=model, optimizer=optimizer, episodes=curr_episode)
        finally:
            if model_save and not interrupted:
                Utils.save_model(model=model, optimizer=optimizer, episodes=curr_episode)

            print(f"White wins: {self.white_wins}; Black wins: {self.black_wins}; Draws: {self.draws};")
            Utils.plot_loss(loss_list=self.loss_list, mode="self-play")


    def update_model(self, model, optimizer):
        optimizer.zero_grad()
        loss = self.compute_loss()
        loss.backward()  # gradients calculation

        torch.nn.utils.clip_grad_norm_(parameters=model.parameters(), max_norm=1.0)

        optimizer.step()  # weights and biases update

        return loss


    def compute_loss(self):
        white_log_probs = torch.stack(self.all_white_log_probs)
        black_log_probs = torch.stack(self.all_black_log_probs)

        if not isinstance(self.all_white_rewards, torch.Tensor):
            self.all_white_rewards = torch.tensor(data=self.all_white_rewards, dtype=torch.float32).to(device=self.device)

        if not isinstance(self.all_black_rewards, torch.Tensor):
            self.all_black_rewards = torch.tensor(data=self.all_black_rewards, dtype=torch.float32).to(device=self.device)

        white_rew_std = self.all_white_rewards.std() + 1e-8
        black_rew_std = self.all_black_rewards.std() + 1e-8

        white_rew_norm = self.all_white_rewards / white_rew_std
        black_rew_norm = self.all_black_rewards / black_rew_std

        white_loss = -(white_log_probs * white_rew_norm).mean()
        black_loss = -(black_log_probs * black_rew_norm).mean()

        # print(f"LOSS DEBUG: White log_probs range: [{white_log_probs.min():.4f}, {white_log_probs.max():.4f}]")
        # print(f"LOSS DEBUG: Black log_probs range: [{black_log_probs.min():.4f}, {black_log_probs.max():.4f}]")

        return white_loss + black_loss


    def collect_episode(self, env: ChessEnv, model):
        observation = env.reset(,

        done = False

        while not done:
            curr_turn = env.board.turn
            observation, white_reward, black_reward, done, info, log_prob = self.make_step(env=env, model=model, observation=observation, device=self.device)

            if curr_turn == chess.WHITE:
                self.all_white_rewards.append(white_reward)
                self.all_white_log_probs.append(log_prob)
            else:
                self.all_black_rewards.append(black_reward)
                self.all_black_log_probs.append(log_prob)


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


    def make_step(self, env, model, observation, device):
        # observation_tensor = (batch_size = 1, channels, height, width)
        observation_tensor = torch.tensor(data=observation, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device=device)

        logits = model(observation_tensor)
        legal_action_idxs = ChessEnvUtils.get_legal_action_idxs(env.board)

        mask = torch.full_like(input=logits, fill_value=float('-inf'))
        mask[0, legal_action_idxs] = 0.0
        masked_logits = logits + mask

        probs = torch.softmax(input=masked_logits, dim=1)
        dist = Categorical(probs=probs)  # discrete distribution

        if np.random.rand() < EPSILON:
            action_chosen = int(np.random.choice(legal_action_idxs))
            action_chosen_tensor = torch.tensor(data=action_chosen, dtype=torch.long, device=logits.device)
            log_prob = torch.log(torch.tensor(data=(1.0 / len(legal_action_idxs)), dtype=torch.float32, device=logits.device)).unsqueeze(0)
        else:
            sampled_tensor = dist.sample()
            action_chosen_tensor = sampled_tensor
            log_prob = dist.log_prob(action_chosen_tensor)

        observation, (white_reward, black_reward), done, info = env.step(action_chosen_tensor.item())
        winner = info.get('winner')

        if winner == chess.WHITE:
            self.white_wins += 1
            self.save_game = True
        elif winner == chess.BLACK:
            self.black_wins += 1
            self.save_game = True
        elif winner is None:
            self.draws += 1
            self.save_game = False

        return observation, white_reward, black_reward, done, info, log_prob


    def reset_probs_and_rewards(self):
        self.all_white_log_probs = []
        self.all_black_log_probs = []
        self.all_white_rewards = []
        self.all_black_rewards = []


    def log_training_info(self, episode, eval_score_list, loss):
        if eval_score_list is not None:
            avg_eval = sum(eval_score_list) / len(eval_score_list)
            eval_std = np.std(eval_score_list)
            eval_range = (min(eval_score_list), max(eval_score_list))

            print(f"Eval Score - Avg: {avg_eval:.3f}, Std: {eval_std:.3f}, Range: [{eval_range[0]:.1f}, {eval_range[1]:.1f}]")

            if eval_std < 0.1:
                print("WARNING: Model stuck - very low eval variance!")
        else:
            self.loss_list.append(float(loss))

            print(f"Episode: {episode}")
            print(f"Loss: {loss:.5f}")