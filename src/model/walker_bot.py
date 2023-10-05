from abc import ABCMeta
import math
import time
from typing import List

import pyautogui
from utilities.walker import Area, Path
from utilities.window import Window
from model.runelite_bot import RuneLiteBot, RuneLiteWindow
from utilities.api.morg_http_client import MorgHTTPSocket

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


    def is_at_destination(self, area: Area) -> bool:
        current_position = self.get_player_position()
        bool_x = current_position[0] in range(area[0], area[2] + 1)
        bool_y = current_position[1] in range(area[1], area[3] + 1)

        return bool_x and bool_y


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

        idx = next(i for i in range(len(path) - 1, -1, -1) if (abs(path[i][0] - current_position[0]) <= 13 and abs(path[i][1] - current_position[1]) <= 13))
        new_pos = path[idx]
        return new_pos


    def compute_tiles(self, new_x: int, new_y: int) -> List[float]:
        """
        Returns the range to click from the minimap center in amount of tiles.
        """

        DEGREESPERYAW: float = 360 / 2048
        TILES_PIXELS = 5

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
