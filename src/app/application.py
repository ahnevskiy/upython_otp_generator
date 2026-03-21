import gc
import sys
from machine import Pin, Timer, SoftI2C

from app.configs import config, TICK_PERIOD_MS
from app.otp_generator import OTPGenerator
from app.utils.lcd1602 import LCD1602
from app.utils.time_helper import get_time_shift_from_ntp_server
from app.utils.wifi import WiFi


class Application:
    def __init__(self):
        ### init garbage collector
        gc.enable()
        gc.collect()
        
        ### init LCD
        I2C_bus = SoftI2C(scl=Pin(config.i2c_bus["config"]["scl"]),
                          sda=Pin(config.i2c_bus["config"]["sda"]),
                          freq=config.i2c_bus["config"]["freq"])
        
        lcd = LCD1602(i2c=I2C_bus, addr=config.i2c_bus["lcd"]["i2c_address"])
        
        lcd.backlight(on=True)

        try:
            lcd.print_in_line(f"[start] v{config.app_version}", 0)

            ### init WiFi
            wifi_station = WiFi(config.wifi.ssid, config.wifi.password)

            ### connect WiFi
            lcd.print_in_line(wifi_station.ssid, 0)
            lcd.print_in_line("connecting...", 1)

            wifi_station.connect()

            if not wifi_station.is_connected():
                lcd.print_in_line("connect fail", 1)
                sys.exit(0)

            lcd.print_in_line(f"[{wifi_station.get_ip()}]", 0)
            lcd.print_in_line("wifi connected", 1)

            ### get time-shift from ntp server
            time_shift = get_time_shift_from_ntp_server()

            ### disconnect WiFi
            wifi_station.disconnect()

            ### init otp-generator
            otp_generator = OTPGenerator(config.codes, time_shift, lcd)

            ### init button
            def button_handler(self):
                otp_generator.on_button_pressed()

            board_button = Pin(config.gpio_button, Pin.IN, Pin.PULL_UP)
            board_button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

            ### init main loop

            def main_loop_callback(timer):
                otp_generator.tick()

            main_loop_timer = Timer(1)
            main_loop_timer.deinit()
            main_loop_timer.init(period=TICK_PERIOD_MS,
                                 mode=Timer.PERIODIC,
                                 callback=main_loop_callback)
        except Exception as e:
            lcd.print_in_line("error:", 0)
            lcd.print_in_line(str(e)[:16], 1)
