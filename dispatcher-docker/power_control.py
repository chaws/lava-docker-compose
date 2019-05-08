#!/usr/bin/env python3

import argparse
import serial
import sys
import time


# Some definitions
DEFAULT_BAUD = 115200
DEFAULT_DEVICE = '/dev/ttyACM0'
DEFAULT_TIMEOUT = 0.5
MAGIC_NUMBER = b'Z'
BYTE_ON = b'1'
BYTE_OFF = b'0'
RELAYS = [b'%i' % i for i in range(0, 9)]


# Try to get a hold on to the arduino device
ser = serial.Serial()
def setUpSerialDevice(device=DEFAULT_DEVICE, baud=DEFAULT_BAUD, timeout=DEFAULT_TIMEOUT):
    ser.baudrate = baud
    ser.timeout = timeout
    ser.port = device

    try:
        ser.open()
        if ser.is_open:
            ser.close()
            return True
    except Exception as e:
        print('Could not initialize serial on device %s, with baud rate %i' % (device, baud))
        print(e)
        return False


def sendBytes(relay, state):
    # Make sure port is closed before attempting to play with it
    if ser.is_open:
        ser.close()

    # Open it cleanly
    ser.open()

    # Empty whatever might be in buffers
    ser.read(4096)

    # Send input
    try:
        # Send first magic number (42)
        ser.write(MAGIC_NUMBER)

        # Send what really matters
        ser.write(relay)
        ser.write(state)

        # Repeat magic number (42)
        ser.write(MAGIC_NUMBER)

        # Wait for confirmation
        res = ser.readline()
        return 'ack' in str(res)
    except:
        print('Could not send data to arduino!')
        return False
    finally:
        # Make sure to close it no matter what
        ser.close()


# For some reason, the first attempt to communicate with arduino always fails, don't know why
# check if pyserial can clear this noise
def clearNoise():
    print('Clearing any serial port noise')
    sendBytes(RELAYS[8], BYTE_OFF)
    sendBytes(RELAYS[8], BYTE_OFF)


def sendCommand(relay, command):
    clearNoise()

    if command in ['on', 'off']:
        print('Turning %s relay %i' % (command, relay))
        if sendBytes(RELAYS[relay], BYTE_ON if command == 'on' else BYTE_OFF):
            print('done')
        else:
            print('failed')
            return False
    elif command == 'reset':
        print('Resetting relay %i' % (relay))

        # Turn off
        print('  turning it off')
        if sendBytes(RELAYS[relay], BYTE_OFF):
            print('  done')
        else:
            print('  failed')
            return False

        print('  waiting it to turn off')
        time.sleep(1)

        print('  turning it back on')
        if sendBytes(RELAYS[relay], BYTE_ON):
            print('  done')
        else:
            print('  failed')
            return False
    else:
        return False
    return True


def testArduino():
    print('Testing arduino')

    clearNoise()

    # Go thru each of the relays testing on and off
    for relay in RELAYS[1:]:
        for state in [BYTE_OFF, BYTE_ON]:
            res = sendBytes(relay, state)
            print('  relay %s, state %s -> %s' % (relay, state, res))
            time.sleep(1)

    # Force it to fail
    res = sendBytes(b'9', BYTE_OFF)
    print('  expect relay 9, state 0 to be False -> %s' % res)
    res = sendBytes(RELAYS[1], b'2')
    print('  expect relay 1, state 2 to be False -> %s' % res)


def main():
    parser = argparse.ArgumentParser(description='Switch relays on and off')                                  
    parser.add_argument('-r', '--relay', choices=range(1, 9), type=int, help='target relay: 1 to 8')
    parser.add_argument('-c', '--command', choices=['on', 'off', 'reset'], help='command to send: on, off or reset')
    parser.add_argument('-d', '--device', default=DEFAULT_DEVICE, help='linux device under /dev where arduino is connected, default: %(default)s')
    parser.add_argument('-b', '--baud', default=DEFAULT_BAUD, help='baud rate to set up serial connection, default: %(default)s')
    parser.add_argument('-t', '--timeout', default=DEFAULT_TIMEOUT, help="timeout when waiting for new data to come in, default: %(default)s")
    parser.add_argument('--test', action='store_true', help="test all arduino relays and connection")

    args = parser.parse_args()

    if setUpSerialDevice(args.device, args.baud, args.timeout) is False:
        return -1

    if args.test:
        return testArduino()
    elif args.relay is None or args.command is None:
        parser.print_help()
        return -1

    return 0 if sendCommand(args.relay, args.command) else -1


if __name__ == '__main__':
    sys.exit(main())
