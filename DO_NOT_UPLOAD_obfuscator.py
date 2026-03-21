"""
TOTP secret obfuscator/deobfuscator.
This script is for LOCAL use only. DO NOT upload to the microcontroller.

Algorithm:
  1. Reverse the Base32 key
  2. Chained Caesar cipher:
     - Seed digits used cyclically: seed 5713 → [5,7,1,3]
     - Shift for char[i] = ordinal(prev_original) + seed_digits[i % 4]
       (first char: shift = seed_digits[0])
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


def _seed_digits(seed):
    s = f"{seed:04d}"
    return [int(d) for d in s]


def obfuscate(key, seed):
    reversed_key = key[::-1]
    sd = _seed_digits(seed)
    result = ""
    for i, c in enumerate(reversed_key):
        if i == 0:
            shift = sd[0]
        else:
            prev_orig = reversed_key[i - 1]
            shift = _char_ordinal(prev_orig) + sd[i % 4]
        result += _shift_char(c, shift)
    return result


def deobfuscate(obfuscated_key, seed):
    sd = _seed_digits(seed)
    deciphered = ""
    for i, c in enumerate(obfuscated_key):
        if i == 0:
            shift = sd[0]
        else:
            prev_orig = deciphered[i - 1]
            shift = _char_ordinal(prev_orig) + sd[i % 4]
        deciphered += _shift_char(c, -shift)
    return deciphered[::-1]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage:")
        print(f"  python {sys.argv[0]} obfuscate <BASE32_KEY> <SEED>")
        print(f"  python {sys.argv[0]} deobfuscate <OBFUSCATED_KEY> <SEED>")
        print()
        print("Example:")
        print(f"  python {sys.argv[0]} obfuscate JBSWY3DPEHPK3PXP 5713")
        sys.exit(1)

    command = sys.argv[1]
    key = sys.argv[2].upper()
    seed = int(sys.argv[3])

    if command == "obfuscate":
        result = obfuscate(key, seed)
        print(f"Original:    {key}")
        print(f"Obfuscated:  {result}")
        print()
        print("Verify (deobfuscate back):")
        verify = deobfuscate(result, seed)
        print(f"Restored:    {verify}")
        print(f"Match:       {verify == key}")
    elif command == "deobfuscate":
        result = deobfuscate(key, seed)
        print(f"Obfuscated:  {key}")
        print(f"Original:    {result}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
