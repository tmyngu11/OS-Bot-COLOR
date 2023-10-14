from model.shared.superheat import SuperHeatBot
from model.vulcan.vulcan_bot import VulcanBot


class VulcanSuperheat(SuperHeatBot):
    def __init__(self):
        self.vulcan = VulcanBot()
        super().__init__(game_title=self.vulcan.game_title, window=self.vulcan.win)
