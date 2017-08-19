import time
import struct
import socket
import numpy as np

DST = "192.168.178.35"
PORT = 8266



def send_animation(fragment):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(fragment, (DST, PORT))
    sock.close()

while True:
    animation = ((np.sin(np.linspace(0, 2*np.pi, 30)) + 1) * 128).astype(np.uint8).tobytes()
    print(animation)
    send_animation(animation)
    time.sleep(max(len(animation) / 25 - 0.1, 0.01))

#send_animation(b'\x00')
