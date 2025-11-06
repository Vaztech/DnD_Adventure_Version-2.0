def assign_biomes(geography):
    biomes = []
    for row in geography:
        biome_row = []
        for tile in row:
            terrain = tile["terrain"]
            features = tile["features"]
            
            if "river" in features:
                biome = "river"
            elif "lake" in features:
                biome = "lake"
            elif terrain == "mountain":
                biome = "alpine"
            elif terrain == "hill":
                biome = "forest" if "forest" in features else "grassland"
            else:
                biome = "forest" if "forest" in features else "plains"
                
            biome_row.append(biome)
        biomes.append(biome_row)
    return biomes