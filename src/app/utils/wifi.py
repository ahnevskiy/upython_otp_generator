import network
from time import sleep

WIFI_CONNECTION_TIMEOUT = 30


class WiFi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.station = network.WLAN(network.STA_IF)

    def connect(self):
        if not self.is_connected():
            connection_tries_counter = 0
            self.station.active(True)
            self.station.connect(self.ssid, self.password)
            while not self.is_connected() and connection_tries_counter < WIFI_CONNECTION_TIMEOUT:
                sleep(1)  # s
                connection_tries_counter += 1
    
    def disconnect(self):
        if self.is_connected():
            self.station.active(False)

    def get_ip(self):
        return self.station.ifconfig()[0]
    
    def is_connected(self):
        return self.station.isconnected()
        