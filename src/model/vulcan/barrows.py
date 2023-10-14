import time
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot
import utilities.api.item_ids as ids
import utilities.api.item_ids as item_ids
import utilities.imagesearch as imsearch


class VulcanBarrows(VulcanBot):
    def __init__(self):
        title = "Barrows"
        description = (
            "Automate Barrows"
        )
        super().__init__(bot_title=title, description=description)

        # headless options
        self.runs = 5

    def create_options(self):
        self.options_builder.add_slider_option("runs", "How many times to run?", 1, 50)

    def save_options(self, options: dict):
        for option in options:
            if option == "runs":
                self.runs = options[option]
            elif option == "action":
                self.action = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.options_set = True

    def reset_state(self):
        self.brothers = {
            "Dharok": False,
            "Ahrim": False,
            "Verak": False,
            "Torag": False,
            "Karil": False,
            "Guthan": False,
        }

        self.hidden_brother = None

    def main_loop(self):
        current_run = 0

        self.reset_state()

        start_time = time.time()

        while current_run < self.runs:
            self.__eat_food()

            # loop through brothers and kill them. skip hidden
            for brother, status in self.brothers.items():
                if status:
                    continue

                self.__handle_brother(brother)

                self.brothers[brother] = True

                # now leave
                stairs = self.search_for_tag("stairs", clr.YELLOW)
                self.mouse.move_to(stairs.center())
                self.mouse.click()
                self.wait_for_idle()

            #### do hidden brother ####
            self.log_msg(f"Doing hidden brother: {self.hidden_brother}")
            self.__handle_brother(self.hidden_brother)

            # open last chest to fight
            chest = self.search_for_tag("chest", clr.PINK)
            self.mouse.move_to(chest.center())
            self.mouse.click()

            self.__handle_prayer(self.hidden_brother)
            time.sleep(2)
            self.__handle_combat(self.hidden_brother)

            self.wait_for_idle()
            time.sleep(5)

            # open last chest
            chest = self.search_for_tag("chest", clr.PINK)
            self.mouse.move_to(chest.center())
            self.mouse.click()

            self.wait_for_idle()

            if self.chatbox_action_text("under attack"):
                self.log_msg(f"Need to fight {self.brother}")
                self.__handle_combat(self.hidden_brother)

                # open last chest
                chest = self.search_for_tag("chest", clr.PINK)
                self.mouse.move_to(chest.center())
                self.mouse.click()

            # open loot chest
            chest = self.search_for_tag("chest", clr.PINK)
            self.mouse.move_to(chest.center())
            self.mouse.click()

            time.sleep(2)

            close_loot_path = imsearch.BOT_IMAGES.joinpath("barrows", "close.png")
            close_loot_option = imsearch.search_img_in_rect(image=close_loot_path, rect=self.win.game_view)
            while not close_loot_option:
                chest = self.search_for_tag("chest", clr.PINK)
                self.mouse.move_to(chest.center())
                self.mouse.click()
                time.sleep(1)
                close_loot_option = imsearch.search_img_in_rect(image=close_loot_path, rect=self.win.game_view)

            self.mouse.move_to(close_loot_option.get_center())
            self.mouse.click()

            time.sleep(2)
            chest = self.search_for_tag("chest", clr.PINK)
            self.mouse.move_to(chest.center())
            self.mouse.click()

            time.sleep(2)

            self.reset_state()

            current_run += 1
            self.log_msg(f"Runs Completed: {current_run}")
            self.__restock()

        end_time = time.time() - start_time
        self.log_msg(f"{current_run} runs completed in {end_time}s. Avg time per run: {end_time/current_run}s")

        self.logout()

    def __handle_brother(self, brother):
        locations = {
            "Dharok": [3574, 3295, 3577, 3300],
            "Ahrim": [3563, 3292, 3566, 3286],
            "Verak": [3555, 3296, 3559, 3300],
            "Torag": [3551, 3285, 3556, 3281],
            "Karil": [3564, 3277, 3568, 3274],
            "Guthan": [3575, 3281, 3580, 3285],
        }

        self.toggle_run(True)

        # walk to brother
        brother_area = locations[brother]
        self.log_msg(f"Moving to {brother}")
        self.walk_to_area(brother_area)
        if not self.is_at_destination(brother_area):
            return

        self.__swap_equip(brother)
        self.__eat_food()
        self.drink_prayer_pots()

        self.__use_spade()

        self.__search_sarcophagus(brother)

    def __handle_hidden_tunnel(self, brother):
        hidden_tunnel_path = imsearch.BOT_IMAGES.joinpath("barrows", "barrows_hidden.png")
        hidden_tunnel = imsearch.search_img_in_rect(image=hidden_tunnel_path, rect=self.win.chat, confidence=0)

        if not hidden_tunnel:
            self.__handle_combat(brother)
            return

        self.disable_prayers()

        if not self.hidden_brother:  # first run through to find hidden brother
            self.log_msg(f"Found hidden tunnel at {brother}")
            self.hidden_brother = brother
        else:  # doing the final brother
            self.mouse.move_to(hidden_tunnel.get_center())
            self.mouse.click()

            time.sleep(1)

            # fearless option
            fearless_option_path = imsearch.BOT_IMAGES.joinpath("barrows", "barrows_fearless.png")
            fearless_option = imsearch.search_img_in_rect(image=fearless_option_path, rect=self.win.chat)
            self.mouse.move_to(fearless_option.get_center())
            self.mouse.click()

            time.sleep(2)
            

    def drink_prayer_pots(self):
        current_prayer = self.get_prayer()

        # Use prayer potion if available
        prayer_potion = self.get_first_occurrence([item_ids.PRAYER_POTION1, item_ids.PRAYER_POTION2, item_ids.PRAYER_POTION3, item_ids.PRAYER_POTION4])
        if prayer_potion != [] and current_prayer <= 20:
            self.log_msg("Using Prayer Potion")
            self.mouse.move_to(self.win.inventory_slots[prayer_potion[0]].random_point())
            self.mouse.click()
            time.sleep(2)

    def __handle_prayer(self, brother):
        current_prayer = self.get_prayer()

        # no prayer
        if current_prayer <= 0:
            return

        # open prayer
        self.log_msg("Open Prayer Tab")
        self.mouse.move_to(self.win.cp_tabs[5].get_center())
        self.mouse.click()

        prayer_id = 18
        if brother == "Ahrim":
            prayer_id = 16
        elif brother == "Karil":
            prayer_id = 17

        self.mouse.move_to(self.win.prayers[prayer_id].get_center())
        self.mouse.click()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].get_center())
        self.mouse.click()

    def __handle_combat(self, brother):
        self.log_msg(f"Fighting {brother}")
        # while not fighting, search for brother to fight
        while self.get_is_player_idle() and not self.get_is_in_combat():
            if self.chatbox_action_text("appears to be empty"):
                self.log_msg(f"{brother} already defeated")
                return

            enemy = self.search_for_tag("barrows brother", clr.RED, timeout=5)
            if enemy:
                self.mouse.move_to(enemy.random_point())
                self.mouse.click()
            else:
                self.disable_prayers()
                self.__search_sarcophagus(brother)
                return

        # wait for fight to be over
        while not self.get_is_player_idle(poll_seconds=5) or self.get_is_in_combat() or self.get_animation() in [829]:
            # Heal if low
            self.__eat_food()

            # Use prayer Pots
            self.drink_prayer_pots()

            # handle magic debuff
            if self.chatbox_action_text("Magic level of 50"):
                restore_potion = self.get_first_occurrence([item_ids.SUPER_RESTORE1, item_ids.SUPER_RESTORE2, item_ids.SUPER_RESTORE3, item_ids.SUPER_RESTORE4])
                if restore_potion != [] and self.get_skill_boosted_level("Magic") < 50:
                    self.log_msg("Using Restore Potion")
                    self.mouse.move_to(self.win.inventory_slots[restore_potion[0]].random_point())
                    self.mouse.click()
                    continue
                self.__restock()
                self.__handle_brother(brother)
                return
            
            time.sleep(1)

        self.log_msg("Finished fighting")
        self.disable_prayers()

    def __swap_equip(self, brother):
        self.select_inventory()

        required_weapon = item_ids.IBANS_STAFF_U
        required_chest = item_ids.AHRIMS_ROBETOP
        if brother == "Ahrim":
            required_weapon = item_ids.ADAMANT_KNIFE
            required_chest = item_ids.GUTHIX_DHIDE_BODY

        if not self.get_is_item_equipped(required_weapon):
            item = self.get_first_occurrence(required_weapon)
            if item != -1:
                self.mouse.move_to(self.win.inventory_slots[item].random_point())
                self.mouse.click()

        if not self.get_is_item_equipped(required_chest):
            item = self.get_first_occurrence(required_chest)
            if item != -1:
                self.mouse.move_to(self.win.inventory_slots[item].random_point())
                self.mouse.click()

    def __search_sarcophagus(self, brother):
        sarcophagus = self.search_for_tag("sarcophagus", clr.PINK)
        self.mouse.move_to(sarcophagus.center())
        self.mouse.click()

        self.__handle_prayer(brother)

        self.__handle_hidden_tunnel(brother)

    def __eat_food(self):
        while self.get_hitpoints()[0] < 60:
            food_indexes = self.get_inv_item_indices(item_ids.all_food + item_ids.combo_food)
            if food_indexes:
                self.log_msg("Eating...")
                self.mouse.move_to(self.win.inventory_slots[food_indexes[0]].random_point())
                self.mouse.click()
                if len(food_indexes) > 1:  # eat another if available
                    self.mouse.move_to(self.win.inventory_slots[food_indexes[1]].random_point())
                    time.sleep(2)
                    self.mouse.click()
                time.sleep(1)
            elif self.get_hp() < 40:
                self.logout()

    def __use_spade(self):
        self.log_msg("Using Spade")
        spade = self.get_first_occurrence(ids.SPADE)
        self.mouse.move_to(self.win.inventory_slots[spade].random_point())
        self.mouse.click()
        self.wait_for_idle()

    def __restock(self):

        self.teleport_home()

        self.toggle_run(True)

        self.select_inventory()

        # only use bank if need more food or refresh prayer pots
        if not self.get_is_inv_full() or self.get_if_item_in_inv(item_ids.VIAL):
            home_bank_area = [3093, 3497, 3094, 3493]
            self.use_bank(home_bank_area)

            # finish walking
            self.wait_for_idle()

            if not self.get_is_inv_full():
                food_path = imsearch.BOT_IMAGES.joinpath("items", "Anglerfish_bank.png")
                food = imsearch.search_img_in_rect(image=food_path, rect=self.win.game_view)
                if food:
                    self.mouse.move_to(food.get_center())
                    self.mouse.click()

            if self.get_if_item_in_inv(item_ids.VIAL):
                # deposit empty vials
                vial = self.get_first_occurrence(item_ids.VIAL)
                if vial != -1:
                    self.mouse.move_to(self.win.inventory_slots[vial].random_point())
                    self.mouse.click()

                # take prayer potions
                potions_path = imsearch.BOT_IMAGES.joinpath("items", "Prayer_potion_bank.png")
                potions = imsearch.search_img_in_rect(image=potions_path, rect=self.win.game_view)
                if potions:
                    self.mouse.move_to(potions.get_center())
                    self.mouse.click()

            self.close_bank()

        self.rejuvenate()

        self.use_teleporter("barrows")
