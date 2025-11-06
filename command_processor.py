import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def process_command(game, current_time: float) -> tuple[bool, float]:
    print("> ", end="", flush=True)
    try:
        cmd = input().strip().lower()
        logger.debug(f"Command input: {cmd}")
        if not cmd:
            game.mode = "movement"
            logger.debug("Switched to movement mode")
        elif cmd == "clear path" and hasattr(game, 'debug_mode') and game.debug_mode:
            game.world.map_generator.ensure_walkable_path(game.player_pos[0], game.player_pos[1], game.world.map)
            print(f"{Fore.GREEN}Path cleared at {game.player_pos}!{Style.RESET_ALL}")
            print(game.world.display_map(game.player_pos))
            logger.debug(f"Cleared path at {game.player_pos}")
        else:
            game.handle_command(cmd)
            logger.debug(f"Processed command: {cmd}")
        return game.running, current_time
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Game interrupted. Farewell, traveler!{Style.RESET_ALL}")
        logger.info("Game interrupted by user")
        return False, current_time
    except Exception as e:
        logger.error(f"Error in command mode: {e}")
        print(f"{Fore.RED}Error processing command: {e}{Style.RESET_ALL}")
        return game.running, current_time