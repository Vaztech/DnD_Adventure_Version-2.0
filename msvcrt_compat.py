# dnd_adventure/msvcrt_compat.py
# Cross-platform replacements for a couple of msvcrt functions.

import sys

if sys.platform == "win32":
    import msvcrt as _msvcrt

    msvcrt = _msvcrt

    def kbhit() -> bool:
        return _msvcrt.kbhit()

    def getch() -> str:
        ch = _msvcrt.getch()
        try:
            return ch.decode("utf-8", errors="ignore")
        except Exception:
            return str(ch)
else:
    # Unix-like: emulate kbhit/getch using termios/tty/select
    import sys as _sys
    import termios as _termios
    import tty as _tty
    import select as _select

    msvcrt = None  # sentinel (not required)

    def kbhit() -> bool:
        r, _, _ = _select.select([_sys.stdin], [], [], 0)
        return bool(r)

    def getch() -> str:
        fd = _sys.stdin.fileno()
        old = _termios.tcgetattr(fd)
        try:
            _tty.setraw(fd)
            ch = _sys.stdin.read(1)
        finally:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old)
        return ch
