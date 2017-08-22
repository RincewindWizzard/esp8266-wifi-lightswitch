#!/usr/bin/python3
import time
import struct
import socket
import numpy as np
import hashlib
import numbers
import sys, time, struct, argparse, os, signal
import pyaudio
import wave
"""
This is a simple script to speak to an esp8266 over UDP, which controls a red led strip.
While the LED strip is flashing, the "red alert" sound from Star Trek TNG is played.
"""
PIDFILE = '/tmp/alert.pid'

class LED(object):
    """
    This represents a remote controlled LED, which can have more than one color channel.
    Communication is done over UDP sockets.
    Every packet has a header containing the number of channels in this packet and a sha256 checksum of the payload.
    The communication is at this time monodirectional. You never get a response from the LED controller.
    This might result in unnoticed packet drop. Keep your packets small to avoid being dropped.
    You can assume, that the recieving LED runs at 25 fps, so there is not much data needed.
    Color values are sent as bytes [0-255]. You can also use floats [0.0 - 1.0] to express light values.
    If you do so, the values are logarithmical adjusted for linear brightness perception.
    """
    PACKET_HEADER = '!B32s'
    HEADER_LEN = struct.calcsize(PACKET_HEADER)
    def __init__(self, ip, port=8266, channel=1, fps=25, bufsize=25):
        if ip == None:
            raise ValueError('No destination address given!')
        self.channel = channel
        self.ip = ip
        self.port = port
        self.fps = fps
        self.bufsize = bufsize
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def vision_correction(self, val, b=100):
        """

        :param val: Brightness value [0.0 - 1.0]
        :param b: Base of potency
        :return: Brightness value adjusted to human vision
        """
        val = max(min(1, val), 0)
        return int((b**val - 1)/(b - 1) * 256)

    def on(self):
        """
        Turn on all channels
        """
        self.all(255)

    def off(self):
        """
        Turn off all channels
        """
        self.all(0)

    def _normalize_value(self, value):
        """
        Tries to interpret value as tuple of brightness values and does whatever is needed to do so.
        :param value:
        :return:
        """
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
        self.value([value]*self.channel)

    def value(self, *values):
        self.send_animation([self._normalize_value(v) for v in values])

    def send_animation(self, animation):
        self.socket.sendto(self.encode_animations(self._normalize_value(d) for d in animation), (self.ip, self.port))

    def play_stream(self, animation):
        """
        Plays an animation an waits for completion.
        :param animation: an iterable data structure containing tuples of brightness for every channel
        """
        fragment = []

        for d in animation:
            d = self._normalize_value(d)
            fragment.append(d)
            if len(fragment) > self.bufsize:
                animations = list(zip(*fragment))
                self.send_animation(*animations)
                time.sleep(self.bufsize / self.fps)
                fragment.clear()



    def encode_animations(self, animation):
        """
        Forges a packet containing the animation
        :param animation: An animation containing brightness values as tuple of integers [0 - 255]
        :return: a byte buffer, which can be send to the LED controller
        """
        animation = list(animation)
        channel_count = len(animation[0])
        animation_len = len(animation)
        buffer = bytearray(LED.HEADER_LEN + channel_count * animation_len)

        for i in range(animation_len):
            for c in range(channel_count):
                buffer[LED.HEADER_LEN + i * channel_count + c] = animation[i][c]

        # compute hash
        buffer[0:LED.HEADER_LEN] = struct.pack(LED.PACKET_HEADER, channel_count, hashlib.sha256(buffer[LED.HEADER_LEN:]).digest())
        return buffer

    def __exit__(self):
        self.socket.close()

class AudioFile(object):
    def __init__(self, audio_file):
        with wave.open(audio_file, 'rb') as wf:
            self.audio_data = wf.readframes(os.path.getsize(audio_file))

        self.duration = wf.getnframes() / wf.getframerate()
        audio_player = pyaudio.PyAudio()

        self.audio_stream = audio_player.open(
            format=audio_player.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )


    def play(self):
        self.audio_stream.write(self.audio_data)

def already_running():
    """
    Looks if this programm is already running as another process
    :return:
    """
    running = False
    if os.path.isfile(PIDFILE):
        running = True
        try:
            with open(PIDFILE, 'r') as f:
                os.kill(int(f.read()), signal.SIGINT)
        except:
            running = False
            os.remove(PIDFILE)

    with open(PIDFILE, 'w') as f:
        f.write(str(os.getpid()))
        f.flush()

    return running

def main():
    parser = argparse.ArgumentParser(description='Flash my red light')
    parser.add_argument('--dst', type=str, default=None,
                        help='IP address of LED controller')

    parser.add_argument('--loop', type=int, default=1,
                        help='How many times should the pattern be played')

    parser.add_argument('--audio', action='store_true',
                        help='Play alarm sound')

    parser.add_argument('--toggle', action='store_true',
                        help='Stop if alarm is already running')

    args = parser.parse_args()


    # kill all other instances
    running = already_running()
    if args.toggle and running:
        exit(1)

    led = LED(args.dst)
    audio_file = AudioFile(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'tng_red_alert2.wav'))
    animation = ((np.sin(np.linspace(-np.pi / 2, 2 * np.pi - np.pi / 2, audio_file.duration * led.fps)) + 1) / 2)

    def run():
        led.send_animation(animation)
        if args.audio:
            audio_file.play()

    for _ in range(args.loop):
        run()

    if args.loop == 0:
        while True:
            run()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        ...