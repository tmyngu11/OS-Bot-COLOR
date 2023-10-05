from abc import ABCMeta
import time
from model.walker_bot import WalkerBot
import utilities.color as clr
from model.runelite_bot import RuneLiteWindow
import utilities.imagesearch as imsearch
import utilities.ocr as ocr

class VulcanBot(WalkerBot, metaclass=ABCMeta):
    def __init__(self, bot_title, description) -> None:
        super().__init__("Vulcan", bot_title, description, RuneLiteWindow("Vulcan Reborn"))
    
    def bank_all(self):
        """
        Private method to deposit inventory into bank
        """

        # self.toggle_run(True)

        self.log_msg("Looking for bank")
        bank = self.search_for_tag("bank", clr.CYAN)
        if bank is None:
            self.log_msg("Bank not found")
            self.walk_to_midpoint()
            return
        self.log_msg("Found bank")

        self.mouse.move_to(bank.random_point())
        if not self.click_on_action("Bank"):
            return
        self.log_msg("Using bank")

        # finish walking
        self.wait_for_idle()

        # find deposit all button
        deposit_all_btn = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png"), self.win.game_view)
        if deposit_all_btn is None:
            return
        self.mouse.move_to(deposit_all_btn.random_point())
        self.log_msg("Depositing inventory")
        self.mouse.click()

        close_button = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "close.png"), self.win.game_view)
        self.mouse.move_to(close_button.random_point())
        self.log_msg("Close bank gui")
        self.mouse.click()


    def walk_to_midpoint(self):
        self.log_msg("Walking to midpoint")
        midpoint = self.search_for_tag("midpoint", clr.YELLOW)
        if not midpoint:
            return
        self.mouse.move_to(midpoint.random_point())
        self.mouse.click()
        
        # finish walking
        self.wait_for_idle()

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def search_for_tag(self, tag_name: str, color: clr.Color):
        failed_searches = 0

        # reset zoom
        # pag.press('ctrl')

        self.log_msg(f"Searching for {tag_name}")

        tag = self.get_nearest_tag(color)
        while tag is None:
            failed_searches += 1
            self.move_camera(10)

            if failed_searches % 10 == 0:
                self.log_msg(f"Searching for {tag_name}...")

            if failed_searches > 30:
                # If we've been searching for a whole minute...
                self.log_msg(f"No {tag_name} found.")
                return None
            time.sleep(1)
            tag = self.get_nearest_tag(color)
            continue
        self.log_msg(f"Found {tag_name}")
        return tag
    
    def click_on_action(self, action: str = None) -> bool:
        time.sleep(1)

        if not action:
            self.mouse.click()
            return True

        if self.mouseover_text(contains="Walk"):
            self.log_msg("Too far away")
            self.walk_to_midpoint()
            return False

        if not self.mouseover_text(contains=action):
            self.move_camera(10)
            return False
    
        self.mouse.click()
        return True

    def dismiss_npc(self):
        npc = self.search_for_tag("npc", clr.RED)
        self.mouse.move_to(npc.random_point())
        self.mouse.right_click()
        dismiss_text = ocr.find_text("Dismiss", self.win.game_view, ocr.BOLD_12, [clr.WHITE, clr.PURPLE, clr.ORANGE])
        if dismiss_text == None:
            return
        self.mouse.move_to(dismiss_text[0].random_point(), mouseSpeed="medium")
        self.mouse.click()


    def drop_items(self, item_id):
        slots = self.api_m.get_inv_item_indices(item_id)
        self.drop(slots)
        time.sleep(1)

