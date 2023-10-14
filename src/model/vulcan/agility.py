from model.shared.agility import AgilityBot
from model.vulcan.vulcan_bot import VulcanBot


class VulcanAgility(AgilityBot):
    def __init__(self):
        self.bot = VulcanBot()
        super().__init__(game_title=self.bot.game_title, window=self.bot.win)
