from model.runelite_bot import RuneLiteWindow
from model.shared.mining import MinerBot


class VulcanMiner(MinerBot):
    def __init__(self):
        super().__init__(game_title="Vulcan", window=RuneLiteWindow("Vulcan Reborn"))
