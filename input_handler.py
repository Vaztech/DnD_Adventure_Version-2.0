# dnd_adventure/input_handler.py
"""
Cross-platform input handler.

Returns:
  - "w", "a", "s", "d" for movement
  - "enter" when Enter/Return is pressed
  - any typed command line (when in command mode, handled by main loop)
"""

from .msvcrt_compat import kbhit, getch

# You can customize these mappings if desired.
MOVE_KEYS = {
    "w": "w",
    "a": "a",
    "s": "s",
    "d": "d",
    "W": "w",
    "A": "a",
    "S": "s",
    "D": "d",
}

def handle_input(game) -> str:
    """
    Non-blocking input for movement mode.
    When Enter is pressed, return "enter".
    Otherwise, return one of the expected commands or "" if no input.
    """
    try:
        # Prefer non-blocking single-key reads
        if kbhit():
            ch = getch()
            if ch in ("\r", "\n"):
                return "enter"
            if ch in MOVE_KEYS:
                return MOVE_KEYS[ch]
            # Optional helpers
            if ch in ("h", "H", "?"):
                return "help"
            if ch in ("g", "G"):
                return "debug"
            return ""
        # No key ready
        return ""
    except Exception:
        # Fallback: environments where raw mode isn't available (e.g., some IDE consoles)
        # In that case, just prompt (blocking). You can tailor this to your game's mode.
        try:
            line = input().strip()
        except EOFError:
            return ""
        if line == "":
            return "enter"
        return line
