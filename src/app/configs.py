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
        self.secret = code_dict["secret"]
        self.period = code_dict["period"]
        self.digits = code_dict["digits"]


def read_app_version():
    with open(file=APP_VERSION_FILENAME, mode="r") as handler:
        return handler.read()


class Config:
    def __init__(self, config_dict):
        self.app_version = read_app_version()
        self.wifi = Wifi(config_dict["wifi"])
        self.i2c_bus = config_dict["i2c_bus"]
        self.gpio_button = config_dict["gpio"]["button"]
        self.pin_length = config_dict.get("pin_length", 4)
        if not 1 <= self.pin_length <= 14:
            raise ValueError("pin_length must be between 1 and 14")
        self.codes = []
        for code in config_dict["codes"]:
            self.codes.append(Code(code))

    def deobfuscate_secrets(self, pin):
        for code in self.codes:
            code.secret = self._deobfuscate(code.secret, pin)

    def _deobfuscate(self, secret, pin):
        s = str(pin)
        s = "0" * (self.pin_length - len(s)) + s
        sd = [int(c) for c in s]
        r = ""
        for i in range(len(secret)):
            c = secret[i]
            if i == 0:
                sh = sd[0]
            else:
                d = r[i - 1]
                sh = ((ord(d) - 65) if "A" <= d <= "Z" else (ord(d) - 50)) + sd[i % self.pin_length]
            if "A" <= c <= "Z":
                r += chr((ord(c) - 65 - sh) % 26 + 65)
            elif "2" <= c <= "7":
                r += chr((ord(c) - 50 - sh) % 6 + 50)
            else:
                r += c
        return r


gc.collect()

config = None

with open(file=CONFIGS_FILENAME, mode="r") as handler:
    config_dict = loads(handler.read())
    config = Config(config_dict)
