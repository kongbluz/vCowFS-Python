#!/usr/bin/env python3
import os
import sys
import llfuse
from argparse import ArgumentParser
import subprocess
import time
import signal
import stat
import logging
import errno
import datetime

mountpoint = ''

class Node():
    def __init__(self, name,  data, permision=777, is_dir=False):
        self.is_dir = is_dir
        self.name = name
        self.create_date = datetime.datetime.now()
        self.modify_date = datetime.datetime.now()
        self.permision = permision
        self.child = []
        self.data = ''

    def addChild(self, node):
        self.child.append(node)


#Code from lltest.py need to implement!!
class Vcosfs(llfuse.Operations):
    def __init__(self):
        super(Vcosfs, self).__init__()
        self.hello_name = b"Readdir"
        self.hello_inode = llfuse.ROOT_INODE+1
        self.hello_data = b"hello world\n"

    def getattr(self, inode, ctx=None):
        entry = llfuse.EntryAttributes()
        if inode == llfuse.ROOT_INODE:
            entry.st_mode = (stat.S_IFDIR | 0o755)
            entry.st_size = 0
        elif inode == self.hello_inode:
            entry.st_mode = (stat.S_IFREG | 0o644)
            entry.st_size = len(self.hello_data)
        else:
            raise llfuse.FUSEError(errno.ENOENT)

        stamp = int(1438467123.985654 * 1e9)
        entry.st_atime_ns = stamp
        entry.st_ctime_ns = stamp
        entry.st_mtime_ns = stamp
        entry.st_gid = os.getgid()
        entry.st_uid = os.getuid()
        entry.st_ino = inode

        return entry

    def lookup(self, parent_inode, name, ctx=None):
        if parent_inode != llfuse.ROOT_INODE or name != self.hello_name:
            raise llfuse.FUSEError(errno.ENOENT)
        return self.getattr(self.hello_inode)

    def opendir(self, inode, ctx):
        if inode != llfuse.ROOT_INODE:
            raise llfuse.FUSEError(errno.ENOENT)
        return inode

    def readdir(self, fh, off):
        assert fh == llfuse.ROOT_INODE
        print("ReadDir")
        # only one entry
        if off == 0:
            yield (self.hello_name, self.getattr(self.hello_inode), 1)

    def open(self, inode, flags, ctx):
        if inode != self.hello_inode:
            raise llfuse.FUSEError(errno.ENOENT)
        if flags & os.O_RDWR or flags & os.O_WRONLY:
            raise llfuse.FUSEError(errno.EPERM)
        return inode

    def read(self, fh, off, size):
        assert fh == self.hello_inode
        return self.hello_data[off:off+size]

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

root_node = Node(is_dir=True, name='/', data=None)

def main():
    options = parse_args(sys.argv[1:])
    print("\nMounting Image {} -to-> {} and version period is {}..\n".format(
          options.image, options.mountpoint, options.time))
    global mountpoint
    mountpoint = options.mountpoint
    subprocess.call(["mount", options.image, options.mountpoint])

    testfs = Vcosfs()
    fuse_options = set(llfuse.default_options)
    fuse_options.add('fsname=vcowfs')
    llfuse.init(testfs, options.mountpoint, fuse_options)
    try:
        llfuse.main(workers=1)
    except:
        llfuse.close(unmount=False)
        raise

    llfuse.close()

if __name__ == '__main__':
    main()
