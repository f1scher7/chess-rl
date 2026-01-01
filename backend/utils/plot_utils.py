from typing import List, Dict
from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt
from backend.configs.game_config import GameConfig
from backend.configs.path_config import PathConfig
from backend.configs.training_config import TrainingConfig


class PlotUtils:

    @staticmethod
    def plot_loss(loss_list: List[float], mode: str) -> None:
        episodes = TrainingConfig.EPISODES if TrainingConfig.EPISODES % 2 == 0 else TrainingConfig.EPISODES - 1
        episode_list = [i for i in range(TrainingConfig.INIT_EPISODE - 1, episodes, TrainingConfig.UPDATE_FREQUENCY)]

        file_name = f"{mode}_loss-graph_{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}"
        final_path = Path(PathConfig.SAVED_GRAPHS_PATH_BASE) / file_name

        text_content = PlotUtils.get_text_content()

        plt.figure(figsize=(14, 10))
        plt.plot(episode_list, loss_list, label="Loss", linewidth=2)

        plt.suptitle(text_content["main_title"], fontsize=16, fontweight='bold', y=0.95)
        plt.figtext(0.5, 0.90, text_content["training_params"], ha='center', fontsize=11, style='italic')
        plt.figtext(0.5, 0.87, text_content["exploration_params"], ha='center', fontsize=11, style='italic')
        plt.figtext(0.5, 0.84, text_content["reward_params"], ha='center', fontsize=11, style='italic')

        plt.xlabel("Episodes", fontsize=12)
        plt.ylabel("Loss", fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.subplots_adjust(top=0.80)

        plt.savefig(final_path, dpi=300, bbox_inches='tight')
        print(f"Loss graph was saved to: {final_path}")

        plt.show()


    @staticmethod
    def get_text_content() -> Dict[str, str]:
        return {
            "main_title": "Training Loss",
            "training_params": f"Training: Episodes={TrainingConfig.EPISODES} • LR={TrainingConfig.LEARNING_RATE} • γ={TrainingConfig.GAMMA}",
            "exploration_params": f"Exploration: ε={TrainingConfig.EPSILON} • Update Freq={TrainingConfig.UPDATE_FREQUENCY}",
            "reward_params": f"Rewards: Terminal={GameConfig.TERMINAL_BONUS} • Castling={GameConfig.CASTLING_BONUS} • Eval Scale={GameConfig.CUSTOM_EVAL_SCALING_FACTOR}",
        }