import gc
import utime

from app.configs import TICKS_PER_SECOND, DISPLAY_ACTIVITY_DURATION
from app.utils.totp import calculate_totp
from app.utils.str_helper import str_ljust, progress_bar


class OTPGenerator:
    def __init__(self, codes_list, time_shift, lcd):
        self.time_shift = time_shift
        self.codes_list = codes_list
        self.lcd = lcd
        self.code_index = 0
        self.display_activity_timer = 0
        self.reset_display_activity_timer()
        self.is_display_active = True
        self.password = "000000"
        self.expiry = 0
        self._button_pressed = False
        self._tick_counter = 0

    def get_true_time(self):
        return utime.time() + self.time_shift

    def inc_code_index(self):
        if self.is_display_active:
            self.code_index += 1
            if self.code_index == len(self.codes_list):
                self.code_index = 0

    def get_current_code(self):
        return self.codes_list[self.code_index]

    def calc_expiry(self):
        code = self.get_current_code()
        return code.period - (self.get_true_time() % code.period)

    def update_password(self):
        self.password, self.expiry = calculate_totp(self.get_true_time(),
                                                    self.get_current_code().secret,
                                                    self.get_current_code().period,
                                                    self.get_current_code().digits)

    def print_info(self):
        seconds = str_ljust(f"{self.expiry}", " ", 2)
        progress_bar_str = progress_bar(self.expiry, self.get_current_code().period, 10)

        self.lcd.print_in_line(f"{self.get_current_code().name}:[{self.password}]", 0)
        self.lcd.print_in_line(f"{progress_bar_str} {seconds}s", 1)

    def deactivate_display(self):
       self.is_display_active = False
       self.lcd.backlight(False)
       self.lcd.clear()

    def tick(self):
        if self._button_pressed:
            self._button_pressed = False
            self._handle_button()

        self._tick_counter += 1
        if self._tick_counter < TICKS_PER_SECOND:
            return
        self._tick_counter = 0

        gc.collect()
        if self.is_display_active:
            new_expiry = self.calc_expiry()
            if new_expiry > self.expiry:
                self.update_password()
            self.expiry = new_expiry

            self.print_info()

            if self.display_activity_timer == 0:
                self.deactivate_display()

            self.display_activity_timer -= 1

    def reset_display_activity_timer(self):
        self.display_activity_timer = DISPLAY_ACTIVITY_DURATION

    def on_button_pressed(self):
        self._button_pressed = True

    def reset_button(self):
        self._button_pressed = False

    def _handle_button(self):
        self.reset_display_activity_timer()

        if self.is_display_active:
            self.inc_code_index()
        else:
            self.is_display_active = True
            self.lcd.backlight(True)

        self.update_password()
