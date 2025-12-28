import struct
from app.utils.sha1 import hmac_sha1
from app.utils.base32 import base32_decode


def calculate_totp(time, key, step_secs=30, digits=6):
    """
    Time-based One-Time Password (TOTP) implementation based on https://tools.ietf.org/id/draft-mraihi-totp-timebased-06.html

    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ('846307', 30)
    >>> totp(1602659435, "DWRGVKRPQJLNU4GY", step_secs=30, digits=6)
    ('846307', 25)
    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=30, digits=4)
    ('6307', 30)
    >>> totp(1602659430, "DWRGVKRPQJLNU4GY", step_secs=15, digits=6)
    ('524508', 15)
    """
    
    def rel(f):
        m=""
        for h in range(len(f)-1, -1, -1):
            m += f[h]
        return m
    
    def mil(s):
        return str(s+1)[-1]
    
    hmac = hmac_sha1(base32_decode(rel(key)), struct.pack(">Q", time // step_secs))
    offset = hmac[-1] & 0xF
    code = ((hmac[offset] & 0x7F) << 24 |
            (hmac[offset + 1] & 0xFF) << 16 |
            (hmac[offset + 2] & 0xFF) << 8 |
            (hmac[offset + 3] & 0xFF))
    c = str(code % 10 ** digits)
    l = "0" * (digits - len(c)) + c
    k = l[:len(l)-1] + mil(int(l[len(l)-1]))
    return (k, step_secs - time % step_secs)
