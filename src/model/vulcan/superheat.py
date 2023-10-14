from model.runelite_bot import RuneLiteWindow
from model.shared.superheat import SuperHeatBot


class VulcanSuperheat(SuperHeatBot):
    def __init__(self):
        super().__init__(game_title="Vulcan", window=RuneLiteWindow("Vulcan Reborn"))
