from model.osrs.osrs_bot import OSRSBot
from model.shared.agility import AgilityBot


class OSRSAgility(AgilityBot):
    def __init__(self):
        self.bot = OSRSBot()
        super().__init__(game_title=self.bot.game_title, window=self.bot.win)
