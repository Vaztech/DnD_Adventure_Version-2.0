import logging
from typing import Dict, Optional
from dnd_adventure.race_selector import select_race, select_subrace
from dnd_adventure.class_selector import select_class
from dnd_adventure.stat_roller import roll_stats
from dnd_adventure.spell_selector import select_spells
from dnd_adventure.selection_reviewer import review_selections
from dnd_adventure.character import Character

logger = logging.getLogger(__name__)

def create_player(player_name: str, game: 'Game') -> Character:
    races = game.races
    classes = game.classes
    selections = {
        "race": None,
        "subrace": None,
        "class": None,
        "stats": [],
        "stat_dict": {},
        "spells": {0: [], 1: []},
        "domain": None
    }
    
    # Race selection
    selections["race"] = select_race(races)
    selected_race = next((r for r in races if r.name == selections["race"]), None)
    if selected_race and selected_race.subraces:
        subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
        selections["subrace"] = select_subrace(subrace_names, selected_race)
    
    # Class selection
    selections["class"] = select_class(classes)
    
    # Domain selection for Cleric
    if selections["class"] == "Cleric":
        domains = ["Air", "Death", "Healing", "War"]
        print("\nSelect a Cleric Domain:")
        for i, domain in enumerate(domains, 1):
            print(f"{i}. {domain}")
        while True:
            try:
                choice = int(input("Enter number: ")) - 1
                if 0 <= choice < len(domains):
                    selections["domain"] = domains[choice]
                    break
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Enter a number.")
    
    # Stats
    selections["stats"], selections["stat_dict"] = roll_stats(
        selected_race, selections["subrace"], classes, selections["class"],
        subclass_name=None, character_level=1
    )
    
    # Spells
    spellcasting_classes = ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Psion"]
    if selections["class"] in spellcasting_classes:
        selections["spells"] = select_spells(
            selections["class"], character_level=1, stat_dict=selections["stat_dict"],
            domain=selections["domain"]
        )
    
    # Review selections
    selections = review_selections(selections, races, classes)
    
    # Create character
    character = Character(
        name=player_name,
        race_name=selections["race"],
        subrace_name=selections["subrace"],
        class_name=selections["class"],
        subclass_name=None,
        level=1,
        stat_dict=selections["stat_dict"],
        known_spells=selections["spells"],
        domain=selections["domain"]
    )
    
    logger.debug(f"Character created: {player_name}, {selections['race']}, {selections['class']}")
    return character