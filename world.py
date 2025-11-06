import logging
import random
from typing import Dict, List, Tuple, Optional
from colorama import Fore, Style
from dnd_adventure.map_generator import MapGenerator

logger = logging.getLogger(__name__)

class World:
    def __init__(self, seed: Optional[int] = None, graphics: Dict = None):
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        self.map_generator = MapGenerator(self.seed)
        self.name = self.map_generator.generate_name()
        self.graphics = graphics if graphics else {}
        self.map = self.map_generator.load_or_generate_map()
        if not self.map or "locations" not in self.map or not self.map["locations"]:
            logger.error("Map initialization failed: No valid locations found")
            self.map = {
                "width": 100,
                "height": 100,
                "locations": [[{"x": x, "y": y, "type": "void", "name": "Void", "country": None} for x in range(100)] for y in range(100)]
            }
        self.starting_position = self.get_default_starting_position()
        self.history = self.generate_history()
        logger.debug(f"World initialized with starting position: {self.starting_position}")

    def get_default_starting_position(self) -> Tuple[int, int]:
        # Prefer a dungeon as the starting point
        try:
            for y in range(self.map["height"]):
                for x in range(self.map["width"]):
                    loc = self.map["locations"][y][x]
                    if loc.get("type") == "dungeon":
                        logger.debug(f"Found dungeon at ({x}, {y}) for starting position")
                        return (x, y)
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error accessing map locations: {e}")
        # Fallback to (5, 0)
        logger.warning("No dungeon found, using default starting position (5, 0)")
        return (5, 0)

    def generate_history(self) -> List[Dict]:
        history = []
        num_eras = random.randint(3, 5)
        current_year = 0
        for i in range(num_eras):
            era_length = random.randint(100, 500)
            era = {
                "name": f"Era {i + 1}",
                "start_year": current_year,
                "events": []
            }
            num_events = random.randint(2, 5)
            for j in range(num_events):
                event_year = current_year + random.randint(0, era_length)
                event_desc = random.choice([
                    f"The kingdom of {self.map_generator.generate_name()} is founded by a legendary hero.",
                    f"A great war breaks out between {self.map_generator.generate_name()} and {self.map_generator.generate_name()}.",
                    f"An ancient artifact, the {self.map_generator.generate_name()} Stone, is discovered.",
                    f"The {self.map_generator.generate_name()} Plague devastates the population."
                ])
                era["events"].append({"year": event_year, "desc": event_desc})
            history.append(era)
            current_year += era_length
        return history

    def get_location(self, x: int, y: int) -> Dict:
        if 0 <= y < self.map["height"] and 0 <= x < self.map["width"]:
            return self.map["locations"][y][x]
        return {"type": "void", "name": "Void", "country": None}

    def display_map(self, player_pos: Tuple[int, int]) -> str:
        view_radius = 5
        x, y = player_pos
        map_display = []
        for dy in range(view_radius, -view_radius - 1, -1):
            row = ""
            for dx in range(-view_radius, view_radius + 1):
                map_x, map_y = x + dx, y + dy
                if 0 <= map_x < self.map["width"] and 0 <= map_y < self.map["height"]:
                    tile = self.get_location(map_x, map_y)
                    terrain_type = tile["type"]
                    if (map_x, map_y) == (x, y):
                        row += Fore.RED + "@" + Style.RESET_ALL
                    else:
                        symbol_data = self.graphics.get("terrains", {}).get(terrain_type, {"symbol": "?", "color": "white"})
                        symbol = symbol_data["symbol"]
                        color = symbol_data["color"]
                        if color == "gray":
                            row += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                        elif color == "dark_green":
                            row += Fore.GREEN + symbol + Style.RESET_ALL
                        elif color == "green":
                            row += Fore.GREEN + symbol + Style.RESET_ALL
                        elif color == "light_green":
                            row += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                        elif color == "light_green_ex":
                            row += Fore.LIGHTGREEN_EX + symbol + Style.RESET_ALL
                        elif color == "blue":
                            row += Fore.BLUE + symbol + Style.RESET_ALL
                        elif color == "light_blue_ex":
                            row += Fore.LIGHTBLUE_EX + symbol + Style.RESET_ALL
                        elif color == "cyan":
                            row += Fore.CYAN + symbol + Style.RESET_ALL
                        elif color == "light_cyan_ex":
                            row += Fore.LIGHTCYAN_EX + symbol + Style.RESET_ALL
                        elif color == "yellow":
                            row += Fore.YELLOW + symbol + Style.RESET_ALL
                        elif color == "light_yellow_ex":
                            row += Fore.LIGHTYELLOW_EX + symbol + Style.RESET_ALL
                        elif color == "red":
                            row += Fore.RED + symbol + Style.RESET_ALL
                        elif color == "light_red_ex":
                            row += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                        elif color == "brown":
                            row += Fore.LIGHTRED_EX + symbol + Style.RESET_ALL
                        elif color == "magenta":
                            row += Fore.MAGENTA + symbol + Style.RESET_ALL
                        elif color == "light_magenta_ex":
                            row += Fore.LIGHTMAGENTA_EX + symbol + Style.RESET_ALL
                        elif color == "light_black_ex":
                            row += Fore.LIGHTBLACK_EX + symbol + Style.RESET_ALL
                        elif color == "white":
                            row += Fore.WHITE + symbol + Style.RESET_ALL
                        elif color == "light_white_ex":
                            row += Fore.LIGHTWHITE_EX + symbol + Style.RESET_ALL
                        elif color == "black":
                            row += Fore.BLACK + symbol + Style.RESET_ALL
                        else:
                            print(f"{Fore.YELLOW}Warning: Unsupported color '{color}' for symbol '{symbol}' in terrain.{Style.RESET_ALL}")
                            row += symbol
                else:
                    row += " "
            map_display.append(row)
        return "\n".join(map_display)