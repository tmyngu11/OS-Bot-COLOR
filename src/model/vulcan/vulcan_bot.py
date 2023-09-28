from abc import ABCMeta

from model.runelite_bot import RuneLiteBot, RuneLiteWindow

class VulcanBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("Vulcan", bot_title, description, RuneLiteWindow("Vulcan Reborn"))