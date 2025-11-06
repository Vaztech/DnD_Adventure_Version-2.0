import json
import os
from typing import Dict, Optional
import logging
from dnd_adventure.game_world import GameWorld  # Updated import

logger = logging.getLogger(__name__)

class SaveManager:
    def __init__(self):
        self.save_dir = os.path.join("dnd_adventure", "saves")
        os.makedirs(self.save_dir, exist_ok=True)

    def save_game(self, save_data: Dict, filename: str):
        """Save game data to a file."""
        try:
            save_path = os.path.join(self.save_dir, filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            logger.info(f"Saved game to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save game to {filename}: {e}")
            raise

    def load_game(self, filename: str) -> Dict:
        """Load game data from a file."""
        try:
            save_path = os.path.join(self.save_dir, filename)
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded game from {save_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load game from {filename}: {e}")
            raise

    def list_saves(self) -> list[str]:
        """List all save files."""
        return [f for f in os.listdir(self.save_dir) if f.endswith(".save")]

    def delete_save(self, filename: str) -> bool:
        """Delete a save file."""
        try:
            save_path = os.path.join(self.save_dir, filename)
            os.remove(save_path)
            logger.info(f"Deleted save file {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete save file {filename}: {e}")
            return False