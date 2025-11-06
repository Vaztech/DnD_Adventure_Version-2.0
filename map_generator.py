import random
import os
import pickle
import logging
from typing import Dict, List
from dnd_adventure.paths import get_resource_path

logger = logging.getLogger(__name__)

class MapGenerator:
    def __init__(self, seed: int):
        self.seed = seed
        random.seed(self.seed)

    def load_or_generate_map(self) -> Dict:
        cache_path = os.path.join("dnd_adventure", "map_cache.pkl")
        try:
            with open(cache_path, "rb") as f:
                cached_map = pickle.load(f)
            logger.info("Loaded map from cache.")
            return cached_map
        except Exception as e:
            logger.error(f"Failed to load map cache from {cache_path}: {e}. Regenerating map.")
            new_map = self.generate_map()
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "wb") as f:
                    pickle.dump(new_map, f)
                logger.info(f"Saved generated map to cache at {cache_path}.")
            except Exception as e:
                logger.error(f"Failed to save map cache to {cache_path}: {e}")
            return new_map

    def generate_map(self) -> Dict:
        width, height = 192, 192
        map_data = {
            "width": width,
            "height": height,
            "locations": [],
            "countries": []
        }

        for y in range(height):
            row = []
            for x in range(width):
                terrain = self.generate_terrain(x, y, width, height)
                row.append({
                    "x": x,
                    "y": y,
                    "type": terrain,
                    "name": f"{terrain.capitalize()} at ({x},{y})",
                    "country": None
                })
            map_data["locations"].append(row)

        self.assign_countries(map_data)
        self.ensure_walkable_path(101, 96, map_data)  # Ensure path at player start
        return map_data

    def generate_terrain(self, x: int, y: int, width: int, height: int) -> str:
        perlin = self.perlin_noise(x / 20.0, y / 20.0, self.seed)
        elevation = self.perlin_noise(x / 50.0, y / 50.0, self.seed + 1)
        if elevation > 0.7:
            return "mountain"
        elif perlin < 0.2:
            return random.choice(["river", "lake", "ocean"])
        elif perlin < 0.4:
            return "plains"
        elif perlin < 0.6:
            return "forest"
        elif perlin < 0.7:
            return "dungeon"
        else:
            return "castle"

    def perlin_noise(self, x: float, y: float, seed: int) -> float:
        random.seed(seed + int(x * 1000 + y))
        return random.random()

    def assign_countries(self, map_data: Dict):
        width, height = map_data["width"], map_data["height"]
        num_countries = random.randint(3, 6)
        countries = []
        for i in range(num_countries):
            capital_x, capital_y = random.randint(0, width - 1), random.randint(0, height - 1)
            countries.append({
                "id": i,
                "name": self.generate_name(),
                "capital": (capital_x, capital_y)
            })

        for y in range(height):
            for x in range(width):
                closest_country = min(countries, key=lambda c: (c["capital"][0] - x) ** 2 + (c["capital"][1] - y) ** 2)
                map_data["locations"][y][x]["country"] = closest_country["id"]

        map_data["countries"] = countries

    def generate_name(self) -> str:
        prefixes = ["Eldr", "Thal", "Vyr", "Kael", "Drak", "Fyr"]
        suffixes = ["ion", "stead", "moor", "wyn", "gard", "thyr"]
        return random.choice(prefixes) + random.choice(suffixes)

    def ensure_walkable_path(self, x: int, y: int, map_data: Dict) -> None:
        """Ensure at least one adjacent tile is walkable (not impassable like mountain/ocean)."""
        if 0 <= y < map_data["height"] and 0 <= x < map_data["width"]:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # North, South, East, West
            random.shuffle(directions)
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < map_data["width"] and 0 <= new_y < map_data["height"]:
                    if map_data["locations"][new_y][new_x]["type"] in ["mountain", "ocean"]:
                        map_data["locations"][new_y][new_x]["type"] = "plains"
                        map_data["locations"][new_y][new_x]["name"] = f"Plains at ({new_x},{new_y})"
                        break