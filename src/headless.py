from model.vulcan.woodcutting import VulcanWoodcutter
from model.vulcan.mining import VulcanMiner
from model.vulcan.thieving import VulcanThiever
from OSBC import App

if __name__ == "__main__":
    app = App(test=True)
    app.test(VulcanThiever())