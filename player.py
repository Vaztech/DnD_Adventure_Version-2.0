# dnd_adventure/player.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Player:
    name: str
    race: str
    subrace: Optional[str]
    character_class: str

    # Stats stored as a dict like {"Strength": 10, "Dexterity": 12, ...}
    stats: Dict[str, int] = field(default_factory=dict)

    # Spells stored as {0: ["Light", ...], 1: ["Magic Missile", ...]}
    spells: Dict[int, List[str]] = field(default_factory=lambda: {0: [], 1: []})

    level: int = 1
    features: List[str] = field(default_factory=list)
    subclass: Optional[str] = None

    # Resources / progression
    hit_points: int = 1
    max_hit_points: int = 1
    mp: int = 0
    max_mp: int = 0
    xp: int = 0

    # Optional bag for other flags (alignment, background, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the player for saving."""
        return {
            "name": self.name,
            "race": self.race,
            "subrace": self.subrace,
            "class": self.character_class,
            "stats": self.stats,
            "spells": self.spells,
            "level": self.level,
            "features": self.features,
            "subclass": self.subclass,
            "hit_points": self.hit_points,
            "max_hit_points": self.max_hit_points,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "xp": self.xp,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Rehydrate a player from a save dict."""
        # Some old saves might store stats as a list; normalize to dict if needed.
        stats = data.get("stats", {})
        if isinstance(stats, list):
            names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
            stats = dict(zip(names, stats))

        return cls(
            name=data["name"],
            race=data["race"],
            subrace=data.get("subrace"),
            character_class=data["class"],
            stats=stats,
            spells=data.get("spells", {0: [], 1: []}),
            level=data.get("level", 1),
            features=data.get("features", []),
            subclass=data.get("subclass"),
            hit_points=data.get("hit_points", 1),
            max_hit_points=data.get("max_hit_points", 1),
            mp=data.get("mp", 0),
            max_mp=data.get("max_mp", 0),
            xp=data.get("xp", 0),
            meta=data.get("meta", {}),
        )

    # Convenience helpers
    def add_xp(self, amount: int) -> None:
        self.xp = max(0, self.xp + max(0, amount))

    def heal(self, amount: int) -> None:
        self.hit_points = min(self.max_hit_points, self.hit_points + max(0, amount))

    def spend_mp(self, cost: int) -> bool:
        if cost <= self.mp:
            self.mp -= cost
            return True
        return False
