from abc import ABCMeta
import time

from utilities.api.morg_http_client import MorgHTTPSocket
import utilities.color as clr
from model.runelite_bot import RuneLiteBot
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
from typing import Union
import utilities.api.item_ids as item_ids
from utilities.walker.walker_bot import WalkerBot


class ExtendedRuneLiteBot(RuneLiteBot, metaclass=ABCMeta):
    def __init__(self, game_title, bot_title, description, window) -> None:
        super().__init__(game_title, bot_title, description, window)
        self.morg_api = MorgHTTPSocket()
        self.walker = WalkerBot(self, self.morg_api)
    
    def bank_all(self):
        """
        Private method to deposit inventory into bank
        """

        self.toggle_run(True)

        self.log_msg("Looking for bank")
        bank = self.search_for_tag("bank", clr.CYAN)
        if bank is None:
            self.log_msg("Bank not found")
            return
        self.log_msg("Found bank")

        self.mouse.move_to(bank.random_point())
        if not self.click_on_action("Bank"):
            return
        self.log_msg("Using bank")

        # finish walking
        self.walker.wait_for_idle()

        # find deposit all button
        deposit_all_btn = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png"), self.win.game_view)
        if deposit_all_btn is None:
            return
        self.mouse.move_to(deposit_all_btn.random_point())
        self.log_msg("Depositing inventory")
        self.mouse.click()

        self.close_bank()

    def bank_items(self, items):
        """
        Private method to deposit inventory into bank
        """

        self.toggle_run(True)

        self.log_msg("Looking for bank")
        bank = self.search_for_tag("bank", clr.CYAN)
        if bank is None:
            self.log_msg("Bank not found")
            return
        self.log_msg("Found bank")

        self.mouse.move_to(bank.random_point())
        if not self.click_on_action("Bank"):
            return
        self.log_msg("Using bank")

        # finish walking
        self.walker.wait_for_idle()

        for item in self.morg_api.get_first_occurrence(items):
            self.mouse.move_to(self.win.inventory_slots[item].random_point())
            self.mouse.click()
            time.sleep(1)

        self.close_bank()


    def walk_to_midpoint(self):
        self.log_msg("Walking to midpoint")
        midpoint = self.search_for_tag("midpoint", clr.YELLOW)
        if not midpoint:
            return
        self.mouse.move_to(midpoint.random_point())
        self.mouse.click()
        
        # finish walking
        self.walker.wait_for_idle()

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def search_for_tag(self, tag_name: str, color: clr.Color, timeout = 30):
        failed_searches = 0

        # reset zoom
        # pag.press('ctrl')

        self.log_msg(f"Searching for {tag_name}")

        tag = self.get_nearest_tag(color)
        while tag is None:
            failed_searches += 1
            self.move_camera(30)

            if failed_searches % 10 == 0:
                self.log_msg(f"Searching for {tag_name}...")

            if failed_searches > timeout:
                # If we've been searching for a whole minute...
                self.log_msg(f"No {tag_name} found.")
                return None
            time.sleep(2)
            tag = self.get_nearest_tag(color)
            continue
        self.log_msg(f"Found {tag_name}")
        return tag
    
    def chatbox_action_text(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.BLACK)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.BLACK):
            return True
    
    def click_on_action(self, action: str = None, area = None) -> bool:
        time.sleep(1)

        if not action:
            self.mouse.click()
            return True

        if self.mouseover_text(contains="Walk"):
            self.log_msg("Too far away")
            if area:
                self.walker.walk_to_area(area)
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
        slots = self.morg_api.get_inv_item_indices(item_id)
        self.drop(slots)
        time.sleep(1)


    def close_bank(self):
        close_button = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "close.png"), self.win.game_view)
        self.mouse.move_to(close_button.random_point())
        self.log_msg("Close bank gui")
        self.mouse.click()


    def use_bank(self, area = None):
        self.log_msg("Looking for bank")
        bank = self.search_for_tag("bank", clr.CYAN)
        if bank is None:
            self.log_msg("Bank not found")
            if area:
                self.walker.walk_to_area(area)
                self.use_bank(area)
            return
        self.log_msg("Found bank")

        self.mouse.move_to(bank.random_point())
        if not self.click_on_action("Bank"):
            if area:
                self.walker.walk_to_area(area)
                self.use_bank(area)
            return
        self.log_msg("Using bank")


    def disable_prayers(self):
        current_prayer = self.get_prayer()

        if current_prayer <= 0:
            return

        self.log_msg("Disable Prayers")
        self.mouse.move_to(self.win.prayer_orb.get_center())
        self.mouse.click()
        self.mouse.click()

    def select_inventory(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

    def select_spellbook(self):
        self.log_msg("Selecting Spellbook...")
        self.mouse.move_to(self.win.cp_tabs[6].random_point())
        self.mouse.click()
        time.sleep(1)

    def superheat_ores(self, ore_id):
        self.select_spellbook()

        ores = self.morg_api.get_inv_item_indices(ore_id)
        if not ores:
            return False

        for ore in ores:
            # check if enough nature runes
            if self.morg_api.get_inv_item_stack_amount(item_ids.NATURE_RUNE) == 0:
                return False

            if ore <= 10:
                ore = 10
            elif ore <= 14:
                ore = 14
            self.mouse.move_to(self.win.spellbook_normal[25].get_center())
            self.mouse.click()

            self.mouse.move_to(self.win.inventory_slots[ore].random_point())
            self.mouse.click()
            time.sleep(0.5)

        return True