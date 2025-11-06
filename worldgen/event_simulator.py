import random
import json

def load_races():
    with open('C:\\Users\\Vaz\\Desktop\\dnd_adventure\\dnd_adventure\\data\\races.json') as f:
        all_races = json.load(f)
        valid_races = ["Dwarf", "Elf", "Human", "Orc"]
        return [race for race in all_races if race["name"] in valid_races]

def simulate_events(civs, years=100):
    races_data = load_races()
    events = []
    civ_power_changes = {civ["name"]: 0 for civ in civs}
    
    race_event_types = {
        "Dwarf": ["mining boom", "clan feud", "forging contest"],
        "Elf": ["arcane discovery", "forest ritual", "artistic renaissance"],
        "Orc": ["blood feud", "raid", "warband gathering"],
        "Human": ["trade fair", "political marriage", "religious festival"]
    }
    
    for year in range(1, years + 1):
        civ1, civ2 = random.sample(civs, 2)
        
        base_events = ["war", "treaty", "marriage", "discovery", "plague", "rebellion", "golden age"]
        civ1_events = race_event_types.get(civ1["race"], [])
        civ2_events = race_event_types.get(civ2["race"], [])
        
        all_events = base_events + civ1_events + civ2_events
        event_type = random.choice(all_events)
        
        consequences = {}
        if event_type == "war":
            winner, loser = random.sample([civ1, civ2], 2)
            power_change = random.randint(5, 20)
            winner_pop_change = random.randint(-200, 100)
            loser_pop_change = random.randint(-500, -100)
            consequences = {
                winner["name"]: {"power": power_change, "population": winner_pop_change},
                loser["name"]: {"power": -power_change, "population": loser_pop_change}
            }
            desc = f"In year {year}, {winner['name']} ({winner['race']}) defeated {loser['name']} ({loser['race']}) in war."
        elif event_type == "mining boom":
            if civ1["race"] == "Dwarf":
                consequences = {
                    civ1["name"]: {"power": 5, "population": 200}
                }
                desc = f"In year {year}, {civ1['name']} (Dwarves) experienced a great mining boom."
        else:
            desc = f"In year {year}, the {civ1['name']} ({civ1['race']}) and {civ2['name']} ({civ2['race']}) engaged in a {event_type}."
        
        for civ_name, changes in consequences.items():
            for stat, value in changes.items():
                civ = next(c for c in civs if c["name"] == civ_name)
                if stat == "population":
                    new_population = civ[stat] + value
                    civ[stat] = max(100, new_population)  # Prevent population below 100
                else:
                    civ[stat] += value
                if stat == "power":
                    civ_power_changes[civ_name] += value
        
        events.append({
            "year": year, 
            "type": event_type, 
            "description": desc,
            "consequences": consequences,
            "races_involved": [civ1["race"], civ2["race"]]
        })
    
    return events