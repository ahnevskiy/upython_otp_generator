import gc
from json import loads


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
        self.name = code_dict["name"]
        self.secret = code_dict["secret"][:-1]
        self.steps = code_dict["steps"]
        self.digits = code_dict["digits"]


def read_app_version():
    with open(file=APP_VERSION_FILENAME, mode='r') as handler:
       return handler.read()


class Config:
    def __init__(self, config_dict):
        self.app_version = read_app_version()
        self.wifi = Wifi(config_dict["wifi"])
        self.i2c_bus = config_dict["i2c_bus"]
        self.gpio_button = config_dict["gpio"]["button"]
        self.codes = []
        for code in config_dict["codes"]:
            self.codes.append(Code(code))
            

gc.collect()

config = None

with open(file=CONFIGS_FILENAME, mode='r') as handler:
    config_dict = loads(handler.read())
    config = Config(config_dict)
