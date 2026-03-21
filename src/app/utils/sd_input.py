from machine import Pin
import utime


SD_LENGTH = 4
SD_BLINK_INTERVAL_MS = 500
SD_INPUT_TIMEOUT_MS = 3000
SD_CONFIRM_BLINK_COUNT = 3

class SDInput:
    def __init__(self, lcd, button_pin):
        self.lcd = lcd
        self.button_pin = button_pin
        self.digits = [0] * SD_LENGTH
        self._button_pressed = False

    def _on_button(self, pin):
        self._button_pressed = True

    def read_aps(self):
        self.lcd.print_in_line("Enter your aps:", 0)
        self.button_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_button)

        for pos in range(SD_LENGTH):
            self.digits[pos] = 0
            self._button_pressed = False
            last_press = utime.ticks_ms()
            blink_state = False
            last_blink = utime.ticks_ms()
            self._update_display(pos, blink_state)

            while utime.ticks_diff(utime.ticks_ms(), last_press) < SD_INPUT_TIMEOUT_MS:
                if self._button_pressed:
                    self._button_pressed = False
                    self.digits[pos] = (self.digits[pos] + 1) % 10
                    last_press = utime.ticks_ms()
                    blink_state = True
                    last_blink = utime.ticks_ms()
                    self._update_display(pos, blink_state)

                now = utime.ticks_ms()
                if utime.ticks_diff(now, last_blink) >= SD_BLINK_INTERVAL_MS:
                    blink_state = not blink_state
                    last_blink = now
                    self._update_display(pos, blink_state)

                utime.sleep_ms(50)

        self.button_pin.irq(handler=None)
        self._show_confirmation()

        return self.digits[0] * 1000 + self.digits[1] * 100 + self.digits[2] * 10 + self.digits[3]

    def _update_display(self, active_pos, show_digit):
        display = ""
        for i in range(SD_LENGTH):
            if i < active_pos:
                display += str(self.digits[i])
            elif i == active_pos:
                display += str(self.digits[i]) if show_digit else "_"
            else:
                display += "_"
        self.lcd.print_in_line(f"[{display}]", 1)

    def _show_confirmation(self):
        self.lcd.print_in_line("Aps accepted", 0)
        code_str = "".join(str(d) for d in self.digits)
        for i in range(SD_CONFIRM_BLINK_COUNT):
            self.lcd.print_in_line(f"[{code_str}]", 1)
            utime.sleep_ms(SD_BLINK_INTERVAL_MS)
            if i < SD_CONFIRM_BLINK_COUNT - 1:
                self.lcd.print_in_line("[    ]", 1)
                utime.sleep_ms(SD_BLINK_INTERVAL_MS)
