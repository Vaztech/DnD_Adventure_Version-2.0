import logging
from dnd_adventure.utils import load_graphics
from dnd_adventure.room import RoomType

logger = logging.getLogger(__name__)

class MovementHandler:
    def __init__(self, game):
        self.game = game
        self.graphics = load_graphics()
        self.directions = {
            'w': (0, -1),  # Up
            's': (0, 1),   # Down
            'a': (-1, 0),  # Left
            'd': (1, 0)    # Right
        }

    def handle_movement(self, direction):
        logger.debug(f"Handling movement: {direction}")
        if direction not in self.directions:
            logger.error(f"Invalid movement direction: {direction}")
            return False

        # Get current position and map
        current_x, current_y = self.game.player_pos
        dx, dy = self.directions[direction]
        new_x, new_y = current_x + dx, current_y + dy

        # Enforce 5x5 grid bounds (0-4)
        if not (0 <= new_x <= 4 and 0 <= new_y <= 4):
            logger.debug(f"Movement out of bounds: ({new_x}, {new_y})")
            return False

        # Get the current room's map layout
        room = self.game.game_world.rooms.get(self.game.current_room)
        if not room:
            logger.error(f"Invalid room: {self.game.current_room}")
            return False
        map_type = room.room_type.name.lower()  # Convert RoomType enum to string (e.g., 'dungeon')
        if map_type not in self.graphics['maps']:
            logger.error(f"Invalid map type: {map_type}")
            return False

        map_layout = self.graphics['maps'][map_type]['layout']
        map_height = len(map_layout)
        map_width = len(map_layout[0]) if map_height > 0 else 0

        # Check bounds
        if not (0 <= new_x < map_width and 0 <= new_y < map_height):
            logger.debug(f"Movement out of bounds: ({new_x}, {new_y})")
            return False

        # Check if the new position is passable (not a wall)
        target_symbol = map_layout[new_y][new_x]
        map_symbols = self.graphics['maps'][map_type]['symbols']
        target_type = map_symbols.get(target_symbol, {}).get('type', 'wall')

        if target_type == 'wall':
            logger.debug(f"Blocked by wall at ({new_x}, {new_y}): {target_symbol}")
            return False

        # Update position
        self.game.player_pos = (new_x, new_y)
        logger.debug(f"Player moved to: ({new_x}, {new_y})")
        return True