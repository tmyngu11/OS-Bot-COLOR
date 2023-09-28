import time
import pyscreeze as pag
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class VulcanMiner(VulcanBot):
    def __init__(self):
        bot_title = "Miner"
        description = "<Script description here>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 600

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        first_loop = True
        logs = 0
        failed_searches = 0

        # Last inventory slot color when empty
        x, y = self.win.inventory_slots[-1].get_center()
        self.empty_slot_clr = pag.pixel(x, y)
        print(self.empty_slot_clr)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if self.__inv_is_full():
                print("Inventory is full")
                self.__use_bank()
                continue

            # Find an ore
            ore = self.get_nearest_tag(clr.PINK)
            if ore is None:
                failed_searches += 1
                if failed_searches % 10 == 0:
                    self.log_msg("Searching for ores...")
                    self.__walk_to_midpoint()
                if failed_searches > 60:
                    # If we've been searching for a whole minute...
                    self.__logout("No tagged ores found. Logging out.")
                time.sleep(1)
                continue
            failed_searches = 0  # If code got here, an ore was found

            # Click tree and wait to start mining
            self.mouse.move_to(ore.random_point())
            if not self.mouseover_text(contains="Mine"):
                continue
            self.mouse.click()

            if first_loop:
                # Chop for a few seconds to get the Mining plugin to show up
                time.sleep(5)
                first_loop = False

            time.sleep(rd.truncated_normal_sample(1, 10, 2, 2))

            # Wait until we're done chopping
            while self.is_player_doing_action("Mining"):
                time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.stop()

    def __inv_is_full(self):
        """
        Private method to check if inventory is full based on the color of the last inventory slot.
        """
        empty_slot_color = clr.Color([75, 66, 58])
        x, y = self.win.inventory_slots[-1].get_center()
        return pag.pixel(x, y) != self.empty_slot_clr

    def __use_bank(self):
        """
        Private method to deposit inventory is full based on the color of the last inventory slot.
        """
        print("Looking for bank")
        bank = self.get_nearest_tag(clr.CYAN)
        if bank is None:
            print("Bank not found")
            self.__walk_to_midpoint()
            time.sleep(1)
            return

        self.mouse.move_to(bank.random_point())
        if not self.mouseover_text(contains="Use"):
            return
        self.mouse.click()

        time.sleep(5)

        deposit = self.get_nearest_tag(clr.GREEN)

        self.mouse.move_to(deposit.random_point())
        time.sleep(2)
        self.mouse.click()

        close_button = self.get_nearest_tag(clr.PURPLE)
        self.mouse.move_to(close_button.random_point())
        time.sleep(2)
        self.mouse.click()


    def __walk_to_midpoint(self):
        print("Walking to midpoint")
        midpoint = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(midpoint.random_point())
        self.mouse.click()


    def __is_bank_open(self):
        return False