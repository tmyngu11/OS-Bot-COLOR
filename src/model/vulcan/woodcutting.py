import time
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot
import utilities.api.item_ids as ids
import pyautogui as pag


class VulcanWoodcutter(VulcanBot):
    def __init__(self):
        title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them. Make sure you have an empty last inventory slot. Press the play"
            " button."
        )
        super().__init__(bot_title=title, description=description)

        # headless options
        self.running_time = 6000
        self.action = "Bank"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 1000)
        self.options_builder.add_dropdown_option("action", "What to do when inventory is full", ["Bank", "Burn", "Fletch", "Drop"])

    def save_options(self, options: dict):
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
        self.options_set = True

    def main_loop(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        first_loop = True

        # # Last inventory slot color when empty
        # x, y = self.win.inventory_slots[-1].get_center()
        # self.empty_slot_clr = pag.pixel(x, y)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if self.get_is_inv_full():
                self.log_msg("Inventory is full")
                if self.action == "Burn":
                    self.__burn_wood()
                elif self.action == "Bank":
                    self.bank_items(ids.logs)
                elif self.action == "Fletch":
                    self.__fletch_wood()
                elif self.action == "Drop":
                    self.drop_all(ids.logs)
                else:
                    self.log_msg("unknown action")
                continue

            # search for a tree
            tree = self.search_for_tag("trees", clr.PINK)
            if not tree:
                continue

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            if not self.click_on_action("Chop"):
                continue

            if first_loop:
                # Chop for a few seconds to get the Woodcutting plugin to show up
                time.sleep(5)
                first_loop = False

            time.sleep(rd.truncated_normal_sample(1, 10, 2, 2))

            # Wait until we're done chopping
            self.wait_for_idle()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __fletch_wood(self):
        self.log_msg("Start fletching")
        self.wait_for_idle()

        knife = self.get_first_occurrence(ids.KNIFE)
        logs = self.get_first_occurrence(ids.logs)
        logs = [l for l in logs if l != -1]
        if len(logs) == 0:
            self.log_msg("No logs in inventory")
            return
        log = logs[0]

        # use knife
        self.mouse.move_to(self.win.inventory_slots[knife].random_point())
        self.mouse.click()

        # on log
        self.mouse.move_to(self.win.inventory_slots[log].random_point())
        self.mouse.click()

        time.sleep(1)

        pag.press("space")
        
        self.wait_for_idle()

        self.log_msg("Finished Fletching")

    
    def __burn_wood(self):
        self.log_msg("Moving to burn location")

        # Find and move to burn spot
        burn_spot = self.get_nearest_tag(clr.GREEN)
        self.mouse.move_to(burn_spot.random_point())
        self.mouse.click()
        
        self.wait_for_idle()

        # start burning
        for i, slot in enumerate(self.win.inventory_slots):
            # skip tinderbox
            if i == 0:
                continue

            # use tinderbox
            self.mouse.move_to(self.win.inventory_slots[0].random_point())
            self.mouse.click()

            # wait for idle
            self.wait_for_idle()

            # use on wood
            self.mouse.move_to(slot.random_point())
            self.mouse.click()

            if self.chatbox_action_text("light a fire here"):
                print("Cant light a fire")
                break

            # wait for wood to burn
            self.wait_for_idle()

        self.log_msg("Finished firemaking")

