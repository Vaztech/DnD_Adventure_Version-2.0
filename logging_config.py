# dnd_adventure/logging_config.py
import logging
import os
import tempfile
from logging import StreamHandler, FileHandler
from typing import Tuple

def _ensure_dir(path: str) -> bool:
    """Ensure a directory exists; return True if ready."""
    try:
        os.makedirs(path, exist_ok=True)
        # Check writability by attempting to create a tiny temp file
        test_path = os.path.join(path, ".writetest")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_path)
        return True
    except Exception:
        return False

def _pick_logs_location() -> Tuple[str, str]:
    """
    Decide a cross-platform logs dir and file path with fallbacks:
      1) <project_root>/logs/
      2) <home>/dnd_adventure_logs/
      3) <temp>/dnd_adventure_logs/
    Returns: (logs_dir, log_file)
    """
    # project_root: parent of the dnd_adventure/ package
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    candidates = [
        os.path.join(project_root, "logs"),
        os.path.join(os.path.expanduser("~"), "dnd_adventure_logs"),
        os.path.join(tempfile.gettempdir(), "dnd_adventure_logs"),
    ]

    for logs_dir in candidates:
        if _ensure_dir(logs_dir):
            return logs_dir, os.path.join(logs_dir, "dnd_adventure.log")

    # Last resort: current directory (should nearly always work)
    fallback_dir = os.getcwd()
    _ensure_dir(fallback_dir)
    return fallback_dir, os.path.join(fallback_dir, "dnd_adventure.log")

def setup_logging(level: int = logging.INFO) -> None:
    """
    Cross-platform logging setup (macOS/Windows/Linux).
    - Ensures a writable logs directory and file exist (with fallbacks).
    - Writes to file + console.
    - Safe to call multiple times (no duplicate handlers).
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if getattr(logger, "_dnd_handlers_installed", False):
        return

    logs_dir, log_file = _pick_logs_location()

    # Ensure the log file exists (creates it if missing)
    try:
        if not os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== D&D Adventure Log Initialized ===\n")
    except Exception as e:
        # If file creation fails, fallback to console-only logging
        print(f"[Logger] Warning: could not create log file at {log_file}: {e}")
        log_file = None

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (if available)
    if log_file:
        try:
            file_handler = FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"[Logger] Warning: failed to attach file handler: {e}")

    # Console handler (always attach)
    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Mark as configured to prevent duplicates
    logger._dnd_handlers_installed = True  # type: ignore[attr-defined]

    # A couple of helpful startup lines
    logger.info("Logging initialized.")
    logger.info(f"Logs directory: {logs_dir}")
    if log_file:
        logger.info(f"Log file: {log_file}")
    else:
        logger.info("File logging disabled (console only).")
