from pathlib import Path

def ensure_data_dir() -> Path:
    base_dir = Path(__file__).parent.parent  # Adjust to reach dnd_adventure/data
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir