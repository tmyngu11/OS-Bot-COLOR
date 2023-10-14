import time

import pyautogui
from model.shared.extended_runelite_bot import ExtendedRuneLiteBot
import utilities.color as clr
from model.runelite_bot import RuneLiteWindow
import utilities.imagesearch as imsearch


class VulcanBot(ExtendedRuneLiteBot):
    def __init__(self, bot_title, description) -> None:
        super().__init__("Vulcan", bot_title, description, RuneLiteWindow("Vulcan Reborn"))

    def teleport_home(self):
        # open spells
        # self.log_msg("Open Spells Tab")
        # self.mouse.move_to(self.win.cp_tabs[6].get_center())
        # self.mouse.click()

        # self.mouse.move_to(self.win.spellbook_normal[0].get_center())
        # self.mouse.click()
        pyautogui.write("::home")
        pyautogui.press("enter")
        time.sleep(2)

    def rejuvenate(self):
        area = [3094, 3513, 3096, 3510]
        self.walker.walk_to_area(area)

        pool = self.search_for_tag("pool", clr.YELLOW)
        if not pool:
            return
        self.mouse.move_to(pool.random_point())
        self.mouse.click()

        self.walker.wait_for_idle()

    def use_teleporter(self, location: str):
        teleporter_button = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("vulcan", "teleporter_button.png"), self.win.minimap_area)
        if teleporter_button:
            self.mouse.move_to(teleporter_button.random_point())
            self.mouse.click()
        else:
            area = [3085, 3500, 3087, 3503]
            self.walker.walk_to_area(area)

            teleporter = self.search_for_tag("teleporter", clr.GREEN)
            if not teleporter:
                self.use_teleporter(location)
                return
            self.mouse.move_to(teleporter.random_point())
            self.mouse.click()

        self.walker.wait_for_idle()

        pyautogui.write(location)
        pyautogui.press("enter")
        time.sleep(2)

        teleport = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("vulcan", "teleports.png"), self.win.game_view)
        tx, ty = teleport.random_point()
        self.mouse.move_to([tx, ty + 25])
        self.mouse.click()

        self.walker.wait_for_idle()
