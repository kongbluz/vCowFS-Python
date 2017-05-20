#!/usr/bin/env python3
import os
import sys
import llfuse
from argparse import ArgumentParser
import subprocess
import time
import signal
import time

mountpoint = ''

def sigint_handler(signum, frame):
    subprocess.call(["umount", mountpoint])
    print('Unmounted!!')
    sys.exit()


def parse_args(args):
    '''Parse command line'''

    parser = ArgumentParser()

    parser.add_argument('image', type=str,
                        help='Image file location')
    parser.add_argument('mountpoint', type=str,
                        help='Where to mount the file system')
    parser.add_argument('time', type=str,
                        help='time of versioning period')
    return parser.parse_args(args)

signal.signal(signal.SIGINT, sigint_handler)


def main():
    options = parse_args(sys.argv[1:])
    print("\nMounting Image {} -to-> {} and version period is {}..\n".format(
          options.image, options.mountpoint, options.time))
    global mountpoint
    mountpoint = options.mountpoint
    subprocess.call(["mount", options.image, options.mountpoint])
    while(1):
        print('.')
        time.sleep(1)

if __name__ == '__main__':
    main()
