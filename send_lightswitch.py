import time
import struct
import socket
import numpy as np
import hashlib
import numbers

DST = "192.168.178.32"
PORT = 8266
PACKET_HEADER = '!B32s'
HEADER_LEN = struct.calcsize(PACKET_HEADER)

class LED(object):
    def __init__(self, ip, port=8266, channel=1, fps=25, bufsize=25):
        self.channel = channel
        self.ip = ip
        self.port = port
        self.fps = fps
        self.bufsize = bufsize
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def vision_correction(self, val, b=100):
        # 0.0 <= val <= 1.0
        val = max(min(1, val), 0)
        return int((b**val - 1)/(b - 1) * 256)

    def on(self):
        self.all(255)

    def off(self):
        self.all(0)

    def normalize_value(self, value):
        if isinstance(value, numbers.Number):
            value = [value]

        # replace illegal values with 0
        value = [(x if isinstance(x, numbers.Number) else 0) for x in value]

        # if floats are given values are between 0.0 and 1.0
        if any(isinstance(x, float) for x in value):
            value = [self.vision_correction(x) for x in value]

        value = [int(min(max(0, x), 255)) for x in value]
        return value


    def all(self, value):
        self.value(*[value]*self.channel)

    def value(self, *values):
        self.send_animation(*[self.normalize_value(v) for v in values])

    def send_animation(self, *animations):
        self.socket.sendto(self.encode_animations(*animations), (self.ip, self.port))

    def play_stream(self, data):
        fragment = []

        for d in data:
            d = self.normalize_value(d)
            fragment.append(d)
            if len(fragment) > self.bufsize:
                animations = list(zip(*fragment))
                self.send_animation(*animations)
                time.sleep(self.bufsize / self.fps)
                fragment.clear()



    def encode_animations(self, *animations):
        animation_count = len(animations)
        animation_len = max([len(animation) for animation in animations])
        buffer = bytearray(HEADER_LEN + sum([len(fragment) for fragment in animations]))

        for i in range(animation_len):
            for j, fragment in enumerate(list(animations)):
                buffer[HEADER_LEN + i * animation_count + j] = fragment[min(len(fragment), i)]

        # compute hash
        buffer[0:HEADER_LEN] = struct.pack(PACKET_HEADER, animation_count, hashlib.sha256(buffer[HEADER_LEN:]).digest())
        return buffer

    def __exit__(self):
        self.socket.close()


def sine():
    t = 0
    while True:
        yield np.sin(2 * np.pi * t / 25 - np.pi / 2)/2 + 1
        t += 1

def triangle():
    t = 0
    while True:
        d = abs((t % 200)-100) / 100
        yield d
        t += 1


led = LED(DST)
#led.on()
#time.sleep(0.5)
#led.off()
#led.play_stream(sine())

for x in np.linspace(0, 1, 100):
    print(x)
    led.all(x)
    time.sleep(0.1)

#while True:
#    animation = (-(np.cos(np.linspace(0, 2*np.pi, 50)) + 1) * 128).astype(np.uint8).tobytes()
#    send_animations(animation, animation, animation)
#    time.sleep(max(len(animation) / 25 - 0.1, 0.01))

#send_animations(b'\x00')
