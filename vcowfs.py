#!/usr/bin/env python3
import os
import sys
import llfuse
from argparse import ArgumentParser

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

def main():
    options = parse_args(sys.argv[1:])
    print("\nMounting Image {} -to-> {} and version period is {}..\n".format(
          options.image, options.mountpoint, options.time))

if __name__ == '__main__':
    main()
