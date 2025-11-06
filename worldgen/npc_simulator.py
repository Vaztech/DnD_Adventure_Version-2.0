import random
import json

def load_races():
    with open('C:\\Users\\Vaz\\Desktop\\dnd_adventure\\dnd_adventure\\data\\races.json') as f:
        all_races = json.load(f)
        valid_races = ["Human", "Elf", "Dwarf", "Orc", "Gnome", "Halfling"]
        return [race for race in all_races if race["name"] in valid_races]

def generate_npcs(civs, count=10):
    races_data = load_races()
    npcs = []
    
    race_names = {
        "Human": ["Aldric", "Elaine", "Godric", "Isolde"],
        "Elf": ["Aelar", "Lyria", "Faelar", "Sylria"],
        "Dwarf": ["Thorin", "Hilda", "Balin", "Frea"],
        "Orc": ["Gorak", "Morga", "Thokk", "Urzha"],
        "Gnome": ["Pip", "Tana", "Fizz", "Mibs"],
        "Halfling": ["Bilbo", "Poppy", "Sam", "Marigold"]
    }
    
    for _ in range(count):
        civ = random.choice(civs)
        race = civ["race"]
        subrace = civ.get("subrace")
        
        names = race_names.get(race, ["Urist", "Althaea", "Durin", "Lirael"])
        
        professions = {
            "Human": ["Knight", "Mage", "Merchant", "Farmer"],
            "Elf": ["Archer", "Druid", "Scholar", "Artisan"],
            "Dwarf": ["Warrior", "Smith", "Miner", "Engineer"],
            "Orc": ["Berserker", "Shaman", "Raider", "Hunter"],
            "Gnome": ["Tinker", "Illusionist", "Alchemist", "Bard"],
            "Halfling": ["Thief", "Cook", "Storyteller", "Herbalist"]
        }.get(race, ["Warrior", "Mage", "Thief", "Smith"])
        
        npc = {
            "name": random.choice(names),
            "race": race,
            "subrace": subrace,
            "civ": civ["name"],
            "profession": random.choice(professions),
            "notable": random.random() < 0.3,
            "traits": random.sample(["Brave", "Cunning", "Wise", "Charismatic"], k=random.randint(1, 2))
        }
        npcs.append(npc)
    return npcs