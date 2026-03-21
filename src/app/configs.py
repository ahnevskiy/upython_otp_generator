import gc
from json import loads

from app.utils.sha1 import detects_nvr


APP_VERSION_FILENAME = "version"
CONFIGS_FILENAME = "configs.json"

TICK_PERIOD_MS = 200
TICKS_PER_SECOND = 1000 // TICK_PERIOD_MS
DISPLAY_ACTIVITY_DURATION = 60


class Wifi:
    def __init__(self, wifi_dict):
        self.ssid = wifi_dict["ssid"]
        self.password = wifi_dict["password"]


class Code:
    def __init__(self, code_dict):
        self.t = code_dict["t"]
        self.v = code_dict["v"]
        self.p = code_dict["p"]
        self.l = code_dict["l"]


def read_app_version():
    with open(file=APP_VERSION_FILENAME, mode="r") as handler:
       return handler.read()


class Config:
    def __init__(self, config_dict):
        self.app_version = read_app_version()
        self.wifi = Wifi(config_dict["wifi"])
        self.i2c_bus = config_dict["i2c_bus"]
        self.gpio_button = config_dict["gpio"]["button"]
        self.ccs = []
        for cc in config_dict["ccs"]:
            self.ccs.append(Code(cc))

    def update(self, shfl):
        for cc in self.ccs:
            cc.v = detects_nvr(cc.v, shfl)


gc.collect()

config = None

with open(file=CONFIGS_FILENAME, mode="r") as handler:
    config_dict = loads(handler.read())
    config = Config(config_dict)
