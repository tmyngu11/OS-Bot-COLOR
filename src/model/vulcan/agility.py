import time
import utilities.color as clr
import utilities.random_util as rd
from model.vulcan.vulcan_bot import VulcanBot
import utilities.api.item_ids as ids
import utilities.api.item_ids as item_ids
import utilities.imagesearch as imsearch


class VulcanAgility(VulcanBot):
    def __init__(self):
        title = "Agility"
        description = (
            "Automate Agility Courses"
        )
        super().__init__(bot_title=title, description=description)

        # headless options
        self.running_time = 5

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.options_set = True

    def main_loop(self):

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            course = self.search_for_tag("course", clr.GREEN)
            self.mouse.move_to(course.center())
            self.mouse.click()

            self.wait_for_idle()

        self.logout()