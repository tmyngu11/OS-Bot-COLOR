import time
from model.shared.extended_runelite_bot import ExtendedRuneLiteBot
import utilities.color as clr
import utilities.api.item_ids as item_ids
import utilities.imagesearch as imsearch


class SuperHeatBot(ExtendedRuneLiteBot):
    def __init__(self, game_title, window):
        bot_title = "Superheat"
        description = "Superheats ores"
        super().__init__(game_title=game_title, bot_title=bot_title, description=description, window=window)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 600

    def create_options(self):
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
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        ore = item_ids.IRON_ORE
        while time.time() - start_time < end_time:
            if not self.superheat_ores(ore):
                break

            self.walker.wait_for_idle()

            self.bank_bars_and_take_ore([item_ids.IRON_BAR], "Iron_ore_bank.png")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.stop()

    def bank_bars_and_take_ore(self, bars, ore_image):
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

        for item in self.morg_api.get_first_occurrence(bars):
            self.mouse.move_to(self.win.inventory_slots[item].random_point())
            self.mouse.click()
            time.sleep(1)

        ore_path = imsearch.BOT_IMAGES.joinpath("items", ore_image)
        banked_ore = imsearch.search_img_in_rect(image=ore_path, rect=self.win.game_view)
        if banked_ore:
            self.mouse.move_to(banked_ore.get_center())
            self.mouse.click()

        self.close_bank()