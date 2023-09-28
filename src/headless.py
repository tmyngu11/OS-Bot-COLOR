from model.vulcan.woodcutting import VulcanWoodcutter
from OSBC import App

if __name__ == "__main__":
    app = App(test=True)
    app.test(VulcanWoodcutter())