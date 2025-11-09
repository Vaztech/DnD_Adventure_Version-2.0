# dnd_adventure/worldgen/timeline_manager.py
"""
Timeline manager

Provides a stable record_timeline(events) API used by world_state.py.
Also includes small helpers to sort/normalize events and to serialize
the timeline if you want to persist it separately later.
"""

from __future__ import annotations
from typing import List, Dict, Any


def _normalize_event(e: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure minimal keys exist so downstream code never KeyErrors."""
    return {
        "year": int(e.get("year", 0)),
        "type": str(e.get("type", "Unknown")),
        "civilization": str(e.get("civilization", "Unknown")),
        "race": str(e.get("race", "Unknown")),
        "description": str(e.get("description", "")),
    }


def _event_sort_key(e: Dict[str, Any]) -> tuple:
    """Sort by year then type for deterministic output."""
    return (e.get("year", 0), e.get("type", ""))


def record_timeline(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a clean, sorted timeline from raw event dicts.

    Parameters
    ----------
    events : list of dict
        Raw events from event_simulator.simulate_events.

    Returns
    -------
    list of dict
        Normalized + sorted events safe for display or persistence.
    """
    if not events:
        return []

    normalized = [_normalize_event(e) for e in events]
    normalized.sort(key=_event_sort_key)
    # Optionally, add an index for pretty printing
    for i, e in enumerate(normalized, start=1):
        e["index"] = i
    return normalized


# Optional helpers if you later want save/load just the timeline
def to_lines(timeline: List[Dict[str, Any]]) -> List[str]:
    return [f"{e['year']:>4} | {e['type']:<12} | {e['civilization']} — {e['description']}" for e in timeline]


if __name__ == "__main__":
    # Tiny self-test
    demo = [
        {"year": 25, "type": "War", "civilization": "Dwarf Empire", "race": "Dwarf", "description": "Siege of Ironhall"},
        {"year": 3, "type": "Discovery", "civilization": "Elf Dominion", "race": "Elf", "description": "Moonwell found"},
        {"type": "Alliance", "civilization": "Human League", "race": "Human"},  # missing year/desc
    ]
    tl = record_timeline(demo)
    for line in to_lines(tl):
        print(line)
