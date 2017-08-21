import time
import struct
import socket
import numpy as np
import hashlib

DST = "192.168.178.32"
PORT = 8266
PACKET_HEADER = '!B32s'
HEADER_LEN = struct.calcsize(PACKET_HEADER)


def encode_animations(*animations):
    animation_count = len(animations)
    animation_len = max([len(animation) for animation in animations])
    buffer = bytearray(HEADER_LEN + sum([len(fragment) for fragment in animations]))

    for i in range(animation_len):
        for j, fragment in enumerate(list(animations)):
            buffer[HEADER_LEN + i * animation_count + j] = fragment[min(len(fragment), i)]

    # compute hash
    buffer[0:HEADER_LEN] = struct.pack(PACKET_HEADER, animation_count, hashlib.sha256(buffer[HEADER_LEN:]).digest())
    print(buffer)
    return buffer

def send_animations(*fragments):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(encode_animations(*fragments), (DST, PORT))
    sock.close()

while True:
    animation = ((np.sin(np.linspace(0, 2*np.pi, 50)) + 1) * 128).astype(np.uint8).tobytes()
    send_animations(animation, animation, animation)
    time.sleep(max(len(animation) / 25 - 0.1, 0.01))

#send_animation(b'\x00')
