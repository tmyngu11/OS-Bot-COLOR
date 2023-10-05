import time
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot
from utilities.walker import Area, Path


class VulcanMiner(VulcanBot):
    def __init__(self):
        bot_title = "Miner"
        description = "Auto mines ore"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 600

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("action", "What to do when inventory is full", ["Bank", "Drop"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "action":
                self.action = options[option]
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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if self.get_is_inv_full():
                self.log_msg("Inventory is full")
                if self.action == "Bank":
                    self.walk(Path.DWARVEN_MINES_ORE_TO_BANK.value, Area.DWARVEN_MINES_BANK.value)
                    self.bank_all()
                elif self.action == "Drop":
                    self.drop_all(ids.logs)
                else:
                    self.log_msg("unknown action")
                continue

            # Find an ore
            ore = self.search_for_tag("ores", clr.PINK)
            if not ore:
                time.sleep(5)
                continue

            # Click ore and wait to start mining
            self.mouse.move_to(ore.random_point())
            if not self.click_on_action("Mine"):
                continue

            if first_loop:
                # Chop for a few seconds to get the Mining plugin to show up
                time.sleep(5)
                first_loop = False

            time.sleep(rd.truncated_normal_sample(1, 10, 2, 2))

            # Wait until we're done mining
            self.wait_for_idle()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.stop()
