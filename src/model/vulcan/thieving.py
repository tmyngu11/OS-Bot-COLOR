import time
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot


class VulcanThiever(VulcanBot):
    def __init__(self):
        title = "Thieving"
        description = (
            "This bot steals from a stall"
        )
        super().__init__(bot_title=title, description=description)

        # headless options
        self.running_time = 6000
        self.action = "Bank"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("action", "What to do when inventory is full", ["Bank", "Drop"])

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
            # check for guard
            guard = self.get_nearest_tag(clr.RED)
            if guard:
                self.log_msg("Guard is active")
                # dismiss
                self.dismiss_npc()

            # If inventory is full
            if self.get_is_inv_full():
                self.log_msg("Inventory is full")
                if self.action == "Bank":
                    self.bank_all()
                else:
                    self.log_msg("unknown action")
                continue

            # search for a stall
            tree = self.search_for_tag("stall", clr.PINK)

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            if not self.click_on_action("Steal"):
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


