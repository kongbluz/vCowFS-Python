#!/usr/bin/env python3
import os
import sys

def main():
    image, path, t = sys.argv[1], sys.argv[2], sys.argv[4]
    print("\nMounting Image {} -to-> {} and version period is {}..\n".format(image, path, t))

if __name__ == '__main__':
    main()
