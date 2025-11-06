import logging

logger = logging.getLogger(__name__)

class NPC:
    def __init__(self, name: str, race: str, profession: str, traits: list, dialogue: str = "Greetings, traveler!"):
        self.name = name
        self.race = race
        self.profession = profession
        self.traits = traits
        self.dialogue = dialogue
        logger.debug(f"NPC initialized: {name} ({race}, {profession})")

    def talk(self):
        """Return dialogue for the NPC."""
        logger.debug(f"NPC {self.name} speaking: {self.dialogue}")
        return f"{self.name} the {self.race} {self.profession} says: {self.dialogue}"