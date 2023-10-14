from model.shared.mining import MinerBot
from model.vulcan.vulcan_bot import VulcanBot


class VulcanMiner(MinerBot):
    def __init__(self):
        self.vulcan = VulcanBot()
        super().__init__(game_title=self.vulcan.game_title, window=self.vulcan.win)
