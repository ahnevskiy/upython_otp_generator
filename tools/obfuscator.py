"""
TOTP secret obfuscator/deobfuscator.
This script is for LOCAL use only. DO NOT upload to the microcontroller.

Algorithm:
  Chained Caesar cipher:
    - PIN digits used cyclically: PIN 5713 → [5,7,1,3]
    - Shift for char[i] = ordinal(prev_original) + pin_digits[i % len(pin)]
      (first char: shift = pin_digits[0])
      (letter: A=0..Z=25, digit: 2=0..7=5)
"""


def _char_ordinal(c):
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A')
    elif '2' <= c <= '7':
        return ord(c) - ord('2')


def _shift_char(c, shift):
    if 'A' <= c <= 'Z':
        return chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
    elif '2' <= c <= '7':
        return chr((ord(c) - ord('2') + shift) % 6 + ord('2'))
    raise ValueError(f"Invalid Base32 character: {c}")


def _pin_digits(pin_str):
    return [int(d) for d in pin_str]


def obfuscate(key, pin_str):
    key = key.rstrip("=")
    sd = _pin_digits(pin_str)
    pin_len = len(sd)
    result = ""
    for i, c in enumerate(key):
        if i == 0:
            shift = sd[0]
        else:
            prev_orig = key[i - 1]
            shift = _char_ordinal(prev_orig) + sd[i % pin_len]
        result += _shift_char(c, shift)
    return result


def deobfuscate(obfuscated_key, pin_str):
    obfuscated_key = obfuscated_key.rstrip("=")
    sd = _pin_digits(pin_str)
    pin_len = len(sd)
    deciphered = ""
    for i, c in enumerate(obfuscated_key):
        if i == 0:
            shift = sd[0]
        else:
            prev_orig = deciphered[i - 1]
            shift = _char_ordinal(prev_orig) + sd[i % pin_len]
        deciphered += _shift_char(c, -shift)
    return deciphered


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage:")
        print(f"  python {sys.argv[0]} obfuscate <BASE32_KEY> <PIN>")
        print(f"  python {sys.argv[0]} deobfuscate <OBFUSCATED_KEY> <PIN>")
        print()
        print("Example:")
        print(f"  python {sys.argv[0]} obfuscate JBSWY3DPEHPK3PXP 5713")
        sys.exit(1)

    command = sys.argv[1]
    key = sys.argv[2].upper().rstrip("=")
    pin_str = sys.argv[3]

    if not pin_str.isdigit():
        print(f"Error: PIN must contain only digits, got: {pin_str}")
        sys.exit(1)

    if command == "obfuscate":
        result = obfuscate(key, pin_str)
        print(f"Original:    {key}")
        print(f"Obfuscated:  {result}")
        print()
        print("Verify (deobfuscate back):")
        verify = deobfuscate(result, pin_str)
        print(f"Restored:    {verify}")
        print(f"Match:       {verify == key}")
    elif command == "deobfuscate":
        result = deobfuscate(key, pin_str)
        print(f"Obfuscated:  {key}")
        print(f"Original:    {result}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
