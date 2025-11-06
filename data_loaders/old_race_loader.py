import logging
from typing import Dict
from colorama import Fore, Style
from dnd_adventure.character import Character
from dnd_adventure.races import get_races
from dnd_adventure.classes import get_all_classes
from dnd_adventure.race_selector import select_race, select_subrace
from dnd_adventure.class_selector import select_class
from dnd_adventure.stat_roller import roll_stats
from dnd_adventure.spell_selector import select_spells
from dnd_adventure.selection_reviewer import review_selections
from dnd_adventure.character_display import display_character_sheet, display_initial_lore

logger = logging.getLogger(__name__)

def create_player(name: str, game) -> Character:
    print(f"\n{Fore.CYAN}=== Creating character: {name} ==={Style.RESET_ALL}")
    logger.debug(f"Creating character: {name}")
    selections = {}
    races = get_races()
    selections["race"] = select_race(races)
    selected_race = next((r for r in races if r.name == selections["race"]), None)
    if not selected_race:
        logger.error("Selected race not found")
        raise ValueError("Selected race not found")
    if selected_race.subraces:
        subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
        selections["subrace"] = select_subrace(subrace_names, selected_race)
    else:
        selections["subrace"] = None
    classes = get_all_classes()
    selections["class"] = select_class(classes)
    selections["stats"] = roll_stats(selected_race, selections["subrace"], classes, selections["class"])
    selected_class = next((c for c in classes if c["name"] == selections["class"]), None)
    if selected_class["spellcasting"]:
        selections["spells"] = select_spells(selections["class"])
        # Add default spells for Wizard if none selected
        if selections["class"] == "Wizard" and not any(selections["spells"].values()):
            selections["spells"] = {
                0: ["Detect Magic", "Read Magic", "Light"],  # Cantrips
                1: ["Magic Missile", "Shield"]              # 1st-level spells
            }
    else:
        selections["spells"] = {0: [], 1: []}
    selections = review_selections(selections, races, classes)
    race = next((r for r in races if r.name == selections["race"]), None)
    if selections["subrace"] and selections["subrace"] != "Base " + selections["race"]:
        race.subrace = selections["subrace"]
    dnd_class = selected_class
    stats = selections["stats"]
    spells = selections.get("spells", {0: [], 1: []})
    if not race or not dnd_class:
        logger.error("Selected race or class not found")
        raise ValueError("Selected race or class not found")
    character = Character(
        name=name,
        race_name=selections["race"],
        subrace_name=selections["subrace"] if selections["subrace"] and selections["subrace"] != "Base " + selections["race"] else None,
        class_name=selections["class"],
        stats=stats,
        known_spells=spells
    )
    race.apply_modifiers(character)
    display_character_sheet(character, race, dnd_class)
    logger.debug(f"Character created: {character.name}, {character.race_name}, {character.class_name}")
    display_initial_lore(character, game.world)
    return character