from model.vulcan.woodcutting import VulcanWoodcutter
from model.vulcan.mining import VulcanMiner
from model.vulcan.thieving import VulcanThiever
from model.vulcan.barrows import VulcanBarrows
from model.vulcan.superheat import VulcanSuperheat
from OSBC import App
import pyautogui
pyautogui.FAILSAFE = False

if __name__ == "__main__":
    app = App(test=True)
    app.test(VulcanMiner("RuneLite"))