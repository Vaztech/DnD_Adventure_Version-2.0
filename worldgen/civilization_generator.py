import random
import json

def load_races():
    with open('C:\\Users\\Vaz\\Desktop\\dnd_adventure\\dnd_adventure\\data\\races.json') as f:
        all_races = json.load(f)
        # Filter to races used in original logic
        valid_races = ["Dwarf", "Elf", "Human", "Orc", "Gnome", "Halfling", "Goblin", "Kobold"]
        return [race for race in all_races if race["name"] in valid_races]

def generate_civilizations(biomes, num_civs=4):
    races_data = load_races()
    civs = []
    names = ["Dwarovar", "Thalorien", "Goruk", "Sildareth"]
    
    for i in range(num_civs):
        # Select race and possible subrace
        race_data = random.choice(races_data)
        race_name = race_data["name"]
        
        subrace_name = None
        if race_data["subraces"]:
            subrace_name = random.choice(list(race_data["subraces"].keys()))
        
        # Get biome preferences
        biome_prefs = {
            "Dwarf": ["mountain", "hill"],
            "Elf": ["forest"],
            "Human": ["plains", "grassland"],
            "Orc": ["plains", "hill"],
            "Gnome": ["hill", "forest"],
            "Halfling": ["plains", "grassland"],
            "Goblin": ["hill"],
            "Kobold": ["hill", "mountain"]
        }.get(race_name, ["plains"])
        
        # Find suitable capital location
        max_attempts = 100
        capital = None
        for _ in range(max_attempts):
            x = random.randint(0, len(biomes[0])-1)
            y = random.randint(0, len(biomes)-1)
            biome = biomes[y][x]
            if biome in biome_prefs and biome != "alpine":
                capital = {"x": x, "y": y}
                break
        
        if not capital:
            capital = {"x": random.randint(0, len(biomes[0])-1), 
                      "y": random.randint(0, len(biomes)-1)}
        
        civ = {
            "name": random.choice(names) + f"_{i}",
            "race": race_name,
            "subrace": subrace_name,
            "capital": capital,
            "alignment": random.choice(["Good", "Neutral", "Evil"]),
            "culture": random.choice(["Warlike", "Artisan", "Trader", "Mystic"]),
            "population": random.randint(1000, 5000),
            "power": random.randint(50, 100)
        }
        civs.append(civ)
    return civs