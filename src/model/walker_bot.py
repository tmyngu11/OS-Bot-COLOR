from abc import ABCMeta
import math
import time
from typing import List
import random
import pyautogui
from utilities.walker import Area, Path
from utilities.window import Window
from model.runelite_bot import RuneLiteBot, RuneLiteWindow
from utilities.api.morg_http_client import MorgHTTPSocket
import utilities.imagesearch as imsearch


class WalkerBot(RuneLiteBot, MorgHTTPSocket, metaclass=ABCMeta):

    def __init__(self, game_title, bot_title, description, window: Window = RuneLiteWindow("RuneLite")) -> None:
        super().__init__(game_title, bot_title, description, window)
        MorgHTTPSocket.__init__(self)

    def wait_for_idle(self):
        while not self.get_is_player_idle():
            time.sleep(1)

    def walk(self, path: Path, destination: Area) -> None:
        """
        Walks a path by clicking on the minimap
        """
        self.log_msg("Started walking")

        while True:
            # Get live position.
            new_pos = self.get_target_pos(path)

            # if not at destination and no door on screen, walk. Otherwise stop.
            if self.is_at_destination(destination):
                self.log_msg("We made it!")
                break

            self.log_msg("not at dest")

            # Change position.
            self.change_position(new_pos)
            if new_pos == path[-1]:
                self.wait_for_idle()


    def walk_to_area(self, destination: Area):
        self.log_msg("Started walking")

        self.toggle_run(True)
        
        while True:
            # if not at destination and no door on screen, walk. Otherwise stop.
            if self.is_at_destination(destination):
                self.log_msg("We made it!")
                break

            # Get next position to walk to
            new_pos = self.get_next_pos(destination)
            self.log_msg(f"Moving to new position {new_pos}")

            # Change position.
            self.change_position(new_pos)

            # wait for walking to be done
            self.wait_for_idle()

    def get_random_point_in_area(self, area: Area):
        x1, y1, x2, y2 = area

        # Swap x1 and x2 if x1 is greater than x2
        if x1 > x2:
            x1, x2 = x2, x1

        # Swap y1 and y2 if y1 is greater than y2
        if y1 > y2:
            y1, y2 = y2, y1

        # Generate random x and y coordinates within the specified ranges
        random_x = random.randint(x1, x2)
        random_y = random.randint(y1, y2)

        return [random_x, random_y]

    def get_next_pos(self, destination: Area):
        current_pos = self.get_player_position()
        x1, y1, x2, y2 = destination

        # Calculate the center of the destination rectangle
        dest_center_x = (x1 + x2) // 2
        dest_center_y = (y1 + y2) // 2

        # Calculate the difference between current position and destination center
        dx = dest_center_x - current_pos[0]
        dy = dest_center_y - current_pos[1]

        tile_limit = 10

        # Limit the maximum movement to 13 units in both x and y directions
        if abs(dx) > tile_limit:
            dx = tile_limit if dx > 0 else -tile_limit
        if abs(dy) > tile_limit:
            dy = tile_limit if dy > 0 else -tile_limit

        # Calculate the new position
        new_x = current_pos[0] + dx
        new_y = current_pos[1] + dy

        return [new_x, new_y]

    def is_at_destination(self, area: Area) -> bool:
        current_pos = self.get_player_position()
        x1, y1, x2, y2 = area

        # Ensure x1 is the minimum and x2 is the maximum
        if x1 > x2:
            x1, x2 = x2, x1

        # Ensure y1 is the minimum and y2 is the maximum
        if y1 > y2:
            y1, y2 = y2, y1

        # Check if the current position is within the specified area
        if x1 <= current_pos[0] <= x2 and y1 <= current_pos[1] <= y2:
            return True
        else:
            return False

    def change_position(self, new_pos: List[int]) -> None:
        """
        Clicks the minimap to change position
        """
        tiles = self.compute_tiles(new_pos[0], new_pos[1])
        center_minimap = self.win.minimap.get_center()

        if tiles != []:
            pyautogui.moveTo(center_minimap[0] + tiles[0], center_minimap[1] + tiles[1])
            pyautogui.click()
            self.wait_for_idle()

    def get_target_pos(self, path: Path) -> List[int]:
        """
        Returns furthest possible coord.
        """
        current_position = self.get_player_position()

        tile_limit = 13

        idx = next(i for i in range(len(path) - 1, -1, -1) if (abs(path[i][0] - current_position[0]) <= tile_limit and abs(path[i][1] - current_position[1]) <= tile_limit))
        new_pos = path[idx]

        return new_pos

    def compute_tiles(self, new_x: int, new_y: int) -> List[float]:
        """
        Returns the range to click from the minimap center in amount of tiles.
        """

        DEGREESPERYAW: float = 360 / 2048
        TILES_PIXELS = 4

        # Get live camera data.
        camera_position = self.get_camera_position()

        # Account for anticlockwise OSRS minimap.
        degrees = 360 - DEGREESPERYAW * camera_position['yaw']

        # Turn degrees into pi-radians.
        theta = math.radians(degrees)

        # Turn position difference into pixels difference.
        current_position = self.get_player_position()
        x_reg = (new_x - current_position[0]) * TILES_PIXELS
        y_reg = (current_position[1] - new_y) * TILES_PIXELS

        # Formulas to compute norm of a vector in a rotated coordinate system.
        tiles_x = x_reg * math.cos(theta) + y_reg * math.sin(theta)
        tiles_y = -x_reg * math.sin(theta) + y_reg * math.cos(theta)

        return [round(tiles_x, 1), round(tiles_y, 1)]
