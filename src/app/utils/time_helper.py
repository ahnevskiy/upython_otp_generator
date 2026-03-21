import socket
import struct
import utime


def get_ntp_time(host="pool.ntp.org"):
    try:
        # Формируем NTP-запрос
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B  # Режим запроса

        # Отправляем UDP-пакет
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        addr = socket.getaddrinfo(host, 123)[0][-1]
        sock.sendto(ntp_query, addr)

        # Получаем ответ
        msg = sock.recv(48)
        sock.close()

        # Разбираем NTP-пакет (см. RFC 5905)
        ntp_time = struct.unpack("!12I", msg)[10] - 2208988800
        return ntp_time
    except Exception as e:
        print("NTP error:", e)
        return None


def get_time_shift_from_ntp_server():
    ntp_time = get_ntp_time()
    if ntp_time is None:
        return 0
    return ntp_time - utime.time()
