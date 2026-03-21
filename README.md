# uPython OTP Generator

Hardware TOTP (Time-based One-Time Password) generator built on ESP32 with MicroPython. Displays 2FA codes on a 16x2 LCD, syncs time via NTP, and protects stored secrets with PIN-based encryption.

## Security Disclaimer

The secret obfuscation used in this project is **not cryptographically secure**. It is designed to protect against casual access to the config file (e.g., someone seeing it on screen or finding it on a USB drive). With access to the source code, security reduces to brute-forcing the PIN. The PIN length is configurable from 1 to 14 digits (10 to 10^14 combinations). The default 4-digit PIN (10,000 combinations) can be brute-forced in seconds; a 10+ digit PIN offers significantly more resistance. Do not rely on this as your only layer of security for sensitive accounts. Use this project at your own risk.

## Features

- RFC 6238 compliant TOTP generation
- Multiple TOTP accounts with button-based switching
- NTP time synchronization at boot (the device has no RTC module, so WiFi is required to obtain the current time; after sync, WiFi disconnects)
- 16x2 LCD display with progress bar showing time until code expiry
- PIN-protected secret storage — secrets in config are encrypted, decrypted at boot with a configurable PIN (1-14 digits)
- Auto display off after 60 seconds of inactivity to save power
- Fully offline after initial time sync

## Hardware Requirements

| Component | Description |
|-----------|-------------|
| ESP32 | Any ESP32 dev board |
| LCD 1602 | 16x2 character LCD with I2C backpack (PCF8574) |
| Push button | Momentary push button (active low, internal pull-up used) |

### Default Wiring

| Signal | ESP32 GPIO |
|--------|------------|
| LCD SCL | 22 |
| LCD SDA | 21 |
| Button | 3 |

Pin assignments and I2C frequency are configurable in `configs.json`.

## Software Requirements

- [MicroPython](https://micropython.org/) v1.26+ firmware for ESP32
  - Pre-built firmware binary included: `ESP32_GENERIC-20250911-v1.26.1.bin`
- Python 3.x on host machine (for the obfuscator tool)

## Setup

### 1. Flash MicroPython Firmware

```bash
# Erase flash
esptool.py --chip esp32 erase_flash

# Flash firmware
esptool.py --chip esp32 write_flash -z 0x1000 ESP32_GENERIC-20250911-v1.26.1.bin
```

### 2. Prepare Secrets

Use the included obfuscator to encrypt your TOTP Base32 secrets before putting them in the config. Choose a PIN that you will remember (length must match `pin_length` in your config) — it is your decryption key at boot.

```bash
python tools/obfuscator.py obfuscate <BASE32_SECRET> <PIN>
```

Example:

```bash
python tools/obfuscator.py obfuscate JBSWY3DPEHPK3PXP 5713
# Original:    JBSWY3DPEHPK3PXP
# Obfuscated:  ORURZ4FVYSXC6XNP
#
# Verify (deobfuscate back):
# Restored:    JBSWY3DPEHPK3PXP
# Match:       True
```

To verify / recover a secret:

```bash
python tools/obfuscator.py deobfuscate <OBFUSCATED_SECRET> <PIN>
```

> **Warning:** `tools/obfuscator.py` is for your host PC only. Never upload it to the microcontroller.

### 3. Configure

Copy `src/configs.example.json` to `src/configs.json` and edit it:

```json
{
    "wifi": {
        "ssid": "YourWiFiName",
        "password": "YourWiFiPassword"
    },
    "codes": [
        {
            "name": "GitHub",
            "secret": "ORURZ4FVYSXC6XNP",
            "digits": 6,
            "period": 30
        },
        {
            "name": "Google",
            "secret": "ANOTHER_OBFUSCATED_KEY",
            "digits": 6,
            "period": 30
        }
    ],
    "i2c_bus": {
        "lcd": {
            "i2c_address": 39
        },
        "config": {
            "scl": 22,
            "freq": 40000,
            "sda": 21
        }
    },
    "gpio": {
        "button": 3
    },
    "pin_length": 4
}
```

| Field | Description |
|-------|-------------|
| `codes[].name` | Account display name (up to ~7 chars for LCD) |
| `codes[].secret` | Obfuscated Base32 secret |
| `codes[].digits` | OTP digit count (typically 6) |
| `codes[].period` | Time step in seconds (typically 30) |
| `pin_length` | Number of digits in the PIN, 1-14 (default: 4) |

### 4. Upload to ESP32

Upload the entire `src/` directory to the ESP32 filesystem using [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), [Thonny](https://thonny.org/), or [ampy](https://github.com/scientificiern/ampy):

```bash
# Example with mpremote
mpremote cp -r src/ :
```

## Usage

### Boot Sequence

1. **Power on** — displays firmware version
2. **PIN entry** — enter your PIN using the button (length configured via `pin_length`, 1-14 digits):
   - Press the button to increment the current digit (0-9)
   - After 3 seconds of no input, the digit is confirmed and moves to the next
   - Blinking cursor indicates the active digit position
   - After all digits are entered, a confirmation animation plays
3. **WiFi connect** — connects to configured network, syncs time via NTP, then disconnects
4. **OTP display** — shows the first account's TOTP code with a countdown progress bar

### Controls

| Action | Result |
|--------|--------|
| Press button | Switch to next TOTP account |
| No input for 60s | Display turns off (backlight off) |
| Press button (display off) | Wake display, show current code |

### LCD Layout

```
Line 1: AccountName:[123456]
Line 2: [||||||||  ] 15s
```

## Project Structure

```
.
├── tools/
│   └── obfuscator.py             # Host-only secret encryption tool
├── ESP32_GENERIC-20250911-v1.26.1.bin
├── src/
│   ├── boot.py                   # Bootloader
│   ├── main.py                   # Entry point
│   ├── version                   # App version (1.4.0)
│   ├── configs.example.json      # Configuration template
│   ├── configs.json              # Your config (git-ignored)
│   └── app/
│       ├── application.py        # Main application logic
│       ├── configs.py            # Config parser
│       ├── otp_generator.py      # TOTP display & timer loop
│       └── utils/
│           ├── base32.py         # Base32 decoder
│           ├── lcd1602.py        # LCD 1602 I2C driver
│           ├── pin_input.py      # PIN input UI
│           ├── sha1.py           # SHA-1 / HMAC-SHA1
│           ├── str_helper.py     # String formatting helpers
│           ├── time_helper.py    # NTP time sync
│           ├── totp.py           # TOTP algorithm (RFC 6238)
│           └── wifi.py           # WiFi connection manager
├── .gitignore
├── LICENSE
└── README.md
```

## License

[Unlicense](https://unlicense.org) — public domain. See [LICENSE](LICENSE).
