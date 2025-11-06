import random

def generate_geography(width=50, height=50):
    geography = []
    for y in range(height):
        row = []
        for x in range(width):
            elevation = random.randint(0, 100)
            moisture = random.randint(0, 100)
            
            # Base terrain
            if elevation > 85:
                terrain = "mountain"
            elif elevation > 60:
                terrain = "hill"
            else:
                terrain = "plains"
            
            # Add features
            features = []
            if moisture > 80 and elevation < 70:
                features.append("river")
            if moisture > 60 and terrain in ["plains", "hill"]:
                features.append("forest")
            if random.random() < 0.1:
                features.append("lake")
            
            row.append({
                "x": x, "y": y, 
                "elevation": elevation,
                "moisture": moisture,
                "terrain": terrain,
                "features": features
            })
        geography.append(row)
    return geography