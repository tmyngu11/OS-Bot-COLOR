import time
from model.shared.extended_runelite_bot import ExtendedRuneLiteBot
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from utilities.walker import Area, Path
import utilities.api.item_ids as item_ids


class MinerBot(ExtendedRuneLiteBot):
    def __init__(self, game_title, window):
        bot_title = "Miner"
        description = "Auto mines ore"
        super().__init__(game_title=game_title, bot_title=bot_title, description=description, window=window)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 600
        self.action = "Bank"
        self.starting_area = Area.VARROCK_SOUTH_WEST_MINE
        self.walking_path = Path.VARROCK_EAST_MINE_TO_BANK
        self.bank_area = Area.VARROCK_WEST_BANK

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("action", "What to do when inventory is full", ["Bank", "Drop", "Superheat"])
        self.options_builder.add_dropdown_option("location", "Where to mine", ["Dwarven Mines", "Varrok South West Mine"])

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
            elif option == "location":
                self.location = options[option]
                if self.location == "Varrok South West Mine":
                    self.starting_area = Area.VARROCK_SOUTH_WEST_MINE
                    self.walking_path = Path.VARROCK_EAST_MINE_TO_BANK
                    self.bank_area = Area.VARROCK_WEST_BANK
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
        while time.time() - start_time < end_time:
            # If inventory is full
            if self.morg_api.get_is_inv_full():
                self.log_msg("Inventory is full")
                if self.action == "Bank":
                    self.walker.walk(self.walking_path.value, self.bank_area.value)
                    self.bank_all()
                    self.walker.walk(self.walking_path.value.reverse(), self.starting_area.value)
                elif self.action == "Drop":
                    self.drop_all(ids.logs)
                elif self.action == "Superheat":
                    self.select_spellbook()

                    for ore in self.morg_api.get_inv_item_indices(item_ids.COPPER_ORE):
                        self.mouse.move_to(self.win.spellbook_normal[25].get_center())
                        self.mouse.click()

                        self.mouse.move_to(self.win.inventory_slots[ore].random_point())
                        self.mouse.click()
                        time.sleep(1)

                    if self.morg_api.get_is_inv_full():
                        varrock_east_smith = [3246,3407,3250,3403]
                        self.walker.walk_to_area(east_varrock_bank)

                        # Use anvil
                        anvil = self.search_for_tag("anvil", clr.CYAN)
                        self.mouse.move_to(anvil.random_point())

                        east_varrock_bank = [3250,3420,3254,3419]
                        self.walker.walk_to_area(east_varrock_bank)
                        self.bank_all()

                        south_east_varrock_mine = [3285,3366,3288,3363]
                        self.walker.walk_to_area(south_east_varrock_mine)
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

            time.sleep(rd.truncated_normal_sample(1, 10, 2, 2))

            # Wait until we're done mining
            self.walker.wait_for_idle()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.stop()
