import machine
import network
import socket
import ustruct
import time
import sys
SSID = 'Kalte Fusion'
PASSWORD = 'ceil7VieF5sae5woh1ohleowahsuaw'
PORT = 8266
LED_PIN = 5
PACKET_FMT = '!' + 'B'
PACKET_LEN = ustruct.calcsize(PACKET_FMT)
BUFSIZE = 1024

pin = machine.Pin(LED_PIN, machine.Pin.OUT)
led = machine.PWM(pin)
led.freq(1000)



wlan_client  = network.WLAN(network.STA_IF)
wlan_client.active(True)
print('connecting to network', SSID, '...')
wlan_client.connect(SSID, PASSWORD)

while not wlan_client.isconnected():
    ...
ip, subnet, gateway, dns = wlan_client.ifconfig()
print('network config:', ip, subnet, gateway, dns)

# create a UDP socket and listen on port for incoming messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

print("listening")

try:
    while True:
        msg, src = sock.recvfrom(BUFSIZE)
        print(msg, src)
        for b in msg:
            duty = b * 4
            print(b)
            led.duty(b*4)
            time.sleep_ms(40)
        # if b'ping' is send, answer with b'pong'

except:
    print("Error")
    raise
finally:
    # close this socket whatever happened
    sock.close()

