import logging
from typing import List, Any

logger = logging.getLogger(__name__)

class FeatureManager:
    def get_class_features(self, game: Any, character_class: str) -> List[str]:
        classes = game.classes
        class_data = classes.get(character_class, {})
        features = [f["name"] for f in class_data.get("features", []) if f.get("level", 1) == 1]
        logger.debug(f"Selected features for {character_class}: {features}")
        return features