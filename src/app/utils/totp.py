import struct
from app.utils.sha1 import hmac_sha1
from app.utils.base32 import base32_decode


def calculate_totp(time, key, step_secs=30, digits=6):
    """
    Time-based One-Time Password (TOTP) implementation based on https://tools.ietf.org/id/draft-mraihi-totp-timebased-06.html

    >>> calculate_totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ("846307", 30)
    >>> calculate_totp(1602659435, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ("846307", 25)
    >>> calculate_totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=4)
    ("6307", 30)
    >>> calculate_totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=15, digits=6)
    ("524508", 15)
    """

    hmac = hmac_sha1(base32_decode(key), struct.pack(">Q", time // step_secs))
    offset = hmac[-1] & 0xF
    code = ((hmac[offset] & 0x7F) << 24 |
            (hmac[offset + 1] & 0xFF) << 16 |
            (hmac[offset + 2] & 0xFF) << 8 |
            (hmac[offset + 3] & 0xFF))
    otp = str(code % 10 ** digits)
    otp = "0" * (digits - len(otp)) + otp
    return otp, step_secs - time % step_secs
