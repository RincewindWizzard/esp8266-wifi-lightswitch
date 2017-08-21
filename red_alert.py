#!/usr/bin/python3
import sys, time, struct, argparse, os, signal
import serial
import pyaudio
import wave
"""
* This is a simple script to speak to an esp8266 over UDP, which controls a red led strip.
* While the LED strip is flashing, the "red alert" sound from Star Trek TNG is played.
"""

class RedAlert(object):
    def __init__(self, port_dev, port=8266, play_audio=False,
                 audio_file=os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'tng_red_alert1.wav')):

        self.audio = play_audio
        if play_audio:
            # open audio file and configure audio stream
            with wave.open(audio_file, 'rb') as wf:
                self.audio_file = wf.readframes(os.path.getsize(audio_file))

            self.audio_player = pyaudio.PyAudio()
            self.audio_stream = self.audio_player.open(
                format=self.audio_player.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
        for i in range(2):
            self.play_audio()
            time.sleep(0.3)

    def play_audio(self):
        self.audio_stream.write(self.audio_file)

    def read_packet_number(self):
        read = int(self.port.readline().decode('utf8'))
        # print(self.packet_number, '=?', read)
        return read

    def fade(self, value, duration):
        end = time.time() + duration / 1000
        self.port.write(struct.pack('!BH', value, duration))
        if self.audio and value > self._last_value:
            self.play_audio()
        self.port.flush()
        time.sleep(max(0, end - time.time()))
        self._last_value = value

    def play_pattern(self, pattern):
        for value, duration in pattern:
            # print(value, duration)
            self.fade(value, duration)

    def close(self):
        self.port.close()
        if self.audio:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_player.terminate()


def already_running():
    running = False
    if os.path.isfile(pidfile):
        running = True
        try:
            with open(pidfile, 'r') as f:
                os.kill(int(f.read()), signal.SIGINT)
        except:
            running = False
            os.remove(pidfile)

    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))
        f.flush()

    return running


def main():
    parser = argparse.ArgumentParser(description='Flash my red light')
    parser.add_argument('--tty', type=str, default=None,
                        help='Path to UART device')

    parser.add_argument('--loop', type=int, default=1,
                        help='How many times should the pattern be played')

    parser.add_argument('--audio', action='store_true',
                        help='Play alarm sound')

    parser.add_argument('--toggle', action='store_true',
                        help='Stop if alarm is already running')

    parser.add_argument('pattern', metavar='N', type=int, nargs='+',
                        help='flash pattern')
    args = parser.parse_args()


    # kill all other instances
    running = already_running()
    if args.toggle and running:
        exit(1)

    red_alert = RedAlert(args.tty, 9600, play_audio=args.audio)
    pattern = list(zip(args.pattern[0::2], args.pattern[1::2]))

    def quit(*args):
        try:
            red_alert.fade(0, 1)
            red_alert.close()
        except:
            ...
        exit(0)

    signal.signal(signal.SIGINT, quit)

    try:
        if args.loop == 0:
            while True:
                red_alert.play_pattern(pattern)
        else:
            for i in range(args.loop):
                red_alert.play_pattern(pattern)
    except KeyboardInterrupt as e:
        ...
    quit()


pidfile = '/tmp/alert.pid'
if __name__ == '__main__':
    main()