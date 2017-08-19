import network
import socket
import sys
SSID = 'http://kiel.freifunk.net/'
port = 8266

wlan_client  = network.WLAN(network.STA_IF)
wlan_client.active(True)
print('connecting to network', SSID, '...')
wlan_client.connect(SSID)

while not wlan_client.isconnected():
    ...
ip, subnet, gateway, dns = wlan_client.ifconfig()
print('network config:', ip, subnet, gateway, dns)

# create a UDP socket and listen on port for incoming messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', port))

print("listening")

try:
    #while True:
    msg, src = sock.recvfrom(4)
    #    print(msg, src)
    #    # if b'ping' is send, answer with b'pong'
    #    if msg == b'ping':
    #        sock.sendto(b'pong', src)
    print("try")
except:
    print("Error")
    raise
finally:
    # close this socket whatever happened
    sock.close()

