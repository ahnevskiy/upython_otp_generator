import gc
import utime  

from app.utils.totp import totp
from app.utils.str_helper import str_ljust, progress_bar


DISPLAY_ACTIVITY_DURATION = 60


class OTPGenerator():
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

    def get_true_time(self):
        return utime.time() + self.time_shift

    def inc_code_index(self):
        if self.is_display_active:
            self.code_index += 1
            if self.code_index == len(self.codes_list):
                self.code_index = 0
            
    def get_current_code(self):
        return self.codes_list[self.code_index]
    
    def update_password(self):
        self.password, self.expiry = totp(self.get_true_time(),
                                          self.get_current_code().secret,
                                          self.get_current_code().steps,
                                          self.get_current_code().digits)

    def print_info(self):
        seconds = str_ljust(f"{self.expiry}", " ", 2)
        progress_bar_str = progress_bar(self.expiry, self.get_current_code().steps, 10)
        
        self.lcd.print_in_line(f"{self.get_current_code().name}:[{self.password}]", 0)
        self.lcd.print_in_line(f"{progress_bar_str} {seconds}s", 1)
  
    def deactivate_display(self):
       self.is_display_active = False
       self.lcd.backlight(False)
       self.lcd.clear()

    def generate_password(self):
        if self.is_display_active:
            if self.expiry == 0:
                self.update_password()

            self.print_info()

            if self.display_activity_timer == 0:
                self.deactivate_display()

            self.display_activity_timer -= 1
            self.expiry -= 1

    def reset_display_activity_timer(self):
        self.display_activity_timer = DISPLAY_ACTIVITY_DURATION

    def show_password(self):
        gc.collect()
        
        self.reset_display_activity_timer()
        
        if self.is_display_active:
            self.inc_code_index()
            self.update_password()
        else:
            self.is_display_active = True
            self.lcd.backlight(True)
