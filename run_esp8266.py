import serial
import subprocess

COM_PORT = '/dev/ttyUSB0'
BAUDRATE = 115200

print("upload lightswitch.py")
subprocess.call(['ampy', '-b', str(BAUDRATE), '--port', COM_PORT, 'put', 'esp8266/lightswitch.py'])
print("upload wifi_config.py")
subprocess.call(['ampy', '-b', str(BAUDRATE), '--port', COM_PORT, 'put', 'esp8266/wifi_config.py'])
print("upload main.py")
subprocess.call(['ampy', '-b', str(BAUDRATE), '--port', COM_PORT, 'put', 'esp8266/main.py'])

with serial.Serial(COM_PORT, BAUDRATE) as tty:

    tty.write(b'\x03\x04\r\n')
    tty.flush()
    tty.readline()
    print('Prompt:', tty.readline())
    tty.write(b"\nimport lightswitch\r\n")
    tty.flush()
    while True:
        print(tty.readline().decode("utf-8"))