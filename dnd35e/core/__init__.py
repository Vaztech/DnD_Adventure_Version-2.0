class Monster:
    def __init__(self, name, hit_points, abilities):
        self.name = name
        self.hit_points = hit_points
        self.abilities = abilities
        self.has_darkvision = False

class Item:
    def __init__(self, name):
        self.name = name

class Trap:
    def __init__(self, name):
        self.name = name
        self.disarmed = False
    def trigger(self, character):
        pass

class Puzzle:
    def __init__(self, name):
        self.name = name
        self.solved = False
    def attempt_solution(self, character, solution):
        return False

class LightSource:
    def __init__(self, name, is_active=True):
        self.name = name
        self.is_active = is_active

class NPC:
    def __init__(self, name):
        self.name = name