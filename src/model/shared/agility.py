import time
from model.shared import ExtendedRuneLiteBot
import utilities.color as clr

class AgilityBot(ExtendedRuneLiteBot):
    def __init__(self, game_title, window):
        bot_title = "Agility"
        description = (
            "Automate Agility Courses. Requires Agility Plugin"
        )
        super().__init__(game_title=game_title, bot_title=bot_title, description=description, window=window)

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

            self.walker.wait_for_idle()

        self.logout()