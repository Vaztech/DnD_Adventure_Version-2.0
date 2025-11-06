from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ItemProperty:
    name: str
    description: str
    modifier: Optional[Dict[str, int]] = None

@dataclass
class Item:
    name: str
    category: str  # 'weapon', 'armor', 'shield', 'gear', 'wondrous'
    cost: int  # in gold pieces
    weight: float  # in pounds
    description: str
    properties: List[ItemProperty] = None
    ac_bonus: int = 0  # for armor/shields
    damage: Optional[str] = None  # for weapons
    critical: Optional[str] = None  # for weapons
    range_increment: Optional[int] = None  # for ranged weapons

CORE_ITEMS = {
    "Longsword": Item(
        name="Longsword",
        category="weapon",
        cost=15,
        weight=4,
        description="A versatile one-handed martial weapon",
        properties=[ItemProperty("Martial Weapon", "Proficiency required to use effectively")],
        damage="1d8",
        critical="19-20/x2"
    ),
    "Chain Shirt": Item(
        name="Chain Shirt",
        category="armor",
        cost=100,
        weight=25,
        description="Medium armor made of interlocking metal rings",
        ac_bonus=4,
        properties=[ItemProperty("Armor Check Penalty", "-2 to skill checks")]
    )
}