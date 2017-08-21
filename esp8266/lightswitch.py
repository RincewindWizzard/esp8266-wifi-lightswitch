import machine
import network
import socket
import ustruct
import time
import sys
import uhashlib

import wifi_config

PORT = 8266
LED_PIN = 5
PACKET_HEADER = '!B32s'
HEADER_LEN = ustruct.calcsize(PACKET_HEADER)
BUFSIZE = 1024


def init_leds(*pins):
    # activates PWM on every pin and returns LED-objects
    leds = []
    for pin in pins:
        led = machine.PWM(machine.Pin(pin, machine.Pin.OUT))
        led.freq(1000)
        leds.append(led)
    return leds

def on_data(leds, msg):
    # called every time a packet is recieved
    # decode it and check if hash is correct and display the animation
    header = msg[:HEADER_LEN]
    payload = msg[HEADER_LEN:]
    hash = uhashlib.sha256(payload).digest()

    # stream_count tells how many color channels are contained in this message
    # msg_hash is the hash in the header
    stream_count, msg_hash, = ustruct.unpack(PACKET_HEADER, msg)

    # check if hash is correct (message didnt get corrupted)
    if msg_hash == hash:
        print('Packet')
        for i in range(0, len(payload), stream_count):
            for channel in range(min(len(leds), stream_count)):
                data = payload[i + channel]
                leds[channel].duty(data * 4)
            time.sleep_ms(40)
    else:
        print('Packet rejected')

def lightswitch_server(*leds):
    leds = init_leds(*leds)

    # create a UDP socket and listen on port for incoming messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))

    print("listening")

    try:
        while True:
            msg, src = sock.recvfrom(BUFSIZE)
            print(msg, src)
            on_data(leds, msg)
    except:
        print("Error")
        raise
    finally:
        # close this socket whatever happened
        sock.close()

# start listening for packets and display the animations
lightswitch_server(LED_PIN)