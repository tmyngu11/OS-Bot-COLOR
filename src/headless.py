from model.vulcan.mining import VulcanMiner
from OSBC import App

if __name__ == "__main__":
    app = App(test=True)
    app.test(VulcanMiner())