import torch
from datetime import datetime
from backend.config import SAVED_MODELS_PATH


class Utils:

    @staticmethod
    def get_device():
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @staticmethod
    def save_model(model, optimizer):
        filename = f"chess-rl-by-f1scher7-{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}.pth"
        final_path = SAVED_MODELS_PATH + filename

        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, final_path)

        print(f"Model was saved: {final_path}")


    @staticmethod
    def load_model(model, optimizer, path):
        checkpoint = torch.load(path)

        if model and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])

        if optimizer and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        print(f"Loaded!")


