from model.runelite_bot import RuneLiteWindow
from model.shared.agility import AgilityBot


class VulcanAgility(AgilityBot):
    def __init__(self):
        super().__init__(game_title="Vulcan", window=RuneLiteWindow("Vulcan Reborn"))
