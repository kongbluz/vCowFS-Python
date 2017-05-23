#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import os
import sys

import threading
import llfuse
import inodestruct
from inodestruct import *
import errno
import stat
from time import time , sleep
import logging
from collections import defaultdict
from llfuse import FUSEError
from argparse import ArgumentParser
import pprint
pp = pprint.PrettyPrinter(indent=4)

try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()

deley_time = 0
log = logging.getLogger()

# For Python 2 + 3 compatibility
if sys.version_info[0] == 2:
    def next(it):
        return it.next()
else:
    buffer = memoryview


class Vcowfs(llfuse.Operations):

    def __init__(self):
        super(Vcowfs, self).__init__()
        self.dirPresent = rootdir.id

    def lookup(self, inode_p, name, ctx=None):
        log.debug("lookup ++++ named" + name.decode("utf-8"))
        log.debug(str(inode_p) + "zzzzz")
        if name == '.':
            log.debug('look up chioce : 1')
            inode = inode_p
        elif name == '..':
            # wrong wrong wrong wrong waiting for Dreammmmmmmm ~ ~ ~ ~
            log.debug('look up chioce : 2')
            inode = inode_p
            #
        else:
            log.debug('look up chioce : 3')
            if name.decode("utf-8") not in inodestruct.r_inode.getInodeByID(inode_p).fileTable:
                log.debug('look up chioce : 31111111111')
                raise(llfuse.FUSEError(errno.ENOENT))
            else:
                log.debug('look up chioce : 32222222222')
                inode = inodestruct.r_inode.getInodeByID(inode_p).fileTable[
                                             name.decode("utf-8")]
        log.debug("inode in look up : " + str(inode))
        return self.getattr(inode, ctx)

    def getattr(self, inode, ctx=None):
        log.debug("getattr")
        log.debug("get attr inode# : " + str(inode))
        row = inodestruct.r_inode.getInodeByID(inode)

        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout = 300
        entry.st_mode = row.mode
        entry.st_nlink = row.getNlink()
        entry.st_uid = row.uid
        entry.st_gid = row.gid
        entry.st_rdev = 0
        if row.type == 'dir':
            entry.st_size = 0
        else:
            entry.st_size = row.size

        entry.st_blksize = 512
        entry.st_blocks = 1
        entry.st_atime_ns = row.atime_ns
        entry.st_mtime_ns = row.mtime_ns
        entry.st_ctime_ns = row.ctime_ns

        log.debug(entry.st_mode)
        return entry

    def readlink(self, inode, ctx):
        log.debug("readlink")

    def opendir(self, inode, ctx):
        log.debug("opendir")
        return inode

    def readdir(self, inode, off):
        log.debug("readdir #" + str(inode) + " offff" + str(off))

        if off == 0:
            rootz = inodestruct.r_inode.getInodeByID(inode).fileTable
            parent = inodestruct.r_inode.getInodeByID(inode).parent
            yield (b".", self.getattr(inode), inode)
            if parent == None:
                yield (b"..", self.getattr(inode), inode)
            else:
                yield (b"..", self.getattr(parent), parent)
            # yield  ("..", self.getattr(rootz[name]), rootz[name])
            for name in rootz:
                yield (str.encode(name), self.getattr(rootz[name]), rootz[name])

    def unlink(self, inode_p, name, ctx):
        log.debug("unlink")
        entry = self.lookup(inode_p, name)

        if stat.S_ISDIR(entry.st_mode):
            raise llfuse.FUSEError(errno.EISDIR)

        self._remove(inode_p, name, entry)

    def rmdir(self, inode_p, name, ctx):
        log.debug("rmdir")
        entry = self.lookup(inode_p, name)
        log.debug("id in rmdir is : " + str(entry.st_ino))
        if not stat.S_ISDIR(entry.st_mode):
            raise llfuse.FUSEError(errno.ENOTDIR)

        self._remove(inode_p, name, entry)

    def _remove(self, inode_p, name, entry):
        log.debug("_remove")
        if inodestruct.r_inode.getInodeByID(entry.st_ino).fileTable:
            log.debug("child of this is : " +
                      str(inodestruct.r_inode.getInodeByID(entry.st_ino).fileTable))
            raise llfuse.FUSEError(errno.ENOTEMPTY)

        log.debug("delete from inode# : " + str(inode_p))
        log.debug("delete inode# : " + str(entry.st_ino))
        inodestruct.r_inode.getInodeByID(inode_p).rmInode(name=name.decode("utf-8"))

    def release(self, fh):
        log.debug("release______")


    def symlink(self, inode_p, name, target, ctx):
        log.debug("symlink")
        mode = (stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
        return self._create(inode_p, name, mode, ctx, target=target)

    def rename(self, inode_p_old, name_old, inode_p_new, name_new, ctx):
        log.debug("rename")
        entry_old = self.lookup(inode_p_old, name_old)
        odir = inodestruct.r_inode.getInodeByID(inode_p_old)
        ndir = inodestruct.r_inode.getInodeByID(inode_p_new)

        try:
            entry_new = self.lookup(inode_p_new, name_new)
        except llfuse.FUSEError as exc:
            if exc.errno != errno.ENOENT:
                raise
            target_exists = False
        else:
            target_exists = True

        if target_exists:
            pass
        else:
            nid = odir.fileTable[name_old.decode("utf-8")]
            odir.rmInodeTable(name_old.decode("utf-8"))
            ndir.addInodeTable(name_new.decode("utf-8"), nid)

    def link(self, inode, new_inode_p, new_name, ctx):
        log.debug("link")
        entry_p = self.getattr(new_inode_p)
        if entry_p.st_nlink == 0:
            log.warn('Attempted to create entry %s with unlinked parent %d',
                     new_name, new_inode_p)
            raise FUSEError(errno.EINVAL)

        return self.getattr(inode)

    def setattr(self, inode, attr, fields, fh, ctx):
        log.debug("setattr")
        if fields.update_size:
            n = inodestruct.r_inode.getInodeByID(inode)
            data = n.read()
            if len(data) < attr.st_size:
                data = data + b'\0' * (attr.st_size - len(data))
            else:
                data = data[:attr.st_size]
            print("********************" + data.decode("utf-8"))
            n.write(data)


        if fields.update_mode:
            log.debug("********** permission : " + str(attr.st_mode))
            inodestruct.r_inode.getInodeByID(inode).chmod(attr.st_mode)

        if fields.update_uid:
            inodestruct.r_inode.getInodeByID(inode).uid = attr.st_uid

        if fields.update_gid:
            inodestruct.r_inode.getInodeByID(inode).gid = attr.st_gid

        if fields.update_atime:
            inodestruct.r_inode.getInodeByID(inode).atime_ns = attr.st_atime_ns

        if fields.update_mtime:
            inodestruct.r_inode.getInodeByID(inode).st_mtime_ns = attr.mtime_ns

        return self.getattr(inode)

    def mknod(self, inode_p, name, mode, rdev, ctx):
        log.debug("mknod")
        return self._create(inode_p, name, mode, ctx, rdev=rdev)

    def mkdir(self, inode_p, name, mode, ctx=None):
        log.debug("mkdir")
        x = inodestruct.r_inode.getInodeByID(inode_p).addDir(name.decode("utf-8"))
        if name.decode("utf-8") == 'archive':
              x.isAchive = True
        return self.getattr(x.id)

    def statfs(self, ctx):
        log.debug("statfs")
        stat_ = llfuse.StatvfsData()

        stat_.f_bsize = 512
        stat_.f_frsize = 512

        stat_.f_bfree = max(size // stat_.f_frsize, 1024)
        stat_.f_bavail = stat_.f_bfree

        stat_.f_ffree = max(inodes, 100)
        stat_.f_favail = stat_.f_ffree

        return stat_

    def open(self, inode, flags, ctx):
        log.debug("open")
        return inode

    def access(self, inode, mode, ctx):
        log.debug("access")
        self.dirPresent = inode
        return True

    def create(self, inode_parent, name, mode, flags, ctx=None):
        log.debug("create")
        x = inodestruct.r_inode.getInodeByID(inode_parent)
        print("inode_parent "+str(inode_parent));

        x = inodestruct.r_inode.getInodeByID(inode_parent).addFile(name.decode("utf-8"))
        return (x.id,self.getattr(x.id))

    def read(self, fh, offset, length):
        data = inodestruct.r_inode.getInodeByID(fh).read()
        if data is None:
            data = b''
        return data

    def write(self, fh, offset, buf):
        data = inodestruct.r_inode.getInodeByID(fh).read()
        if data is None:
            data = b''
        data = data[:offset] + buf + data[offset+len(buf):]

        inodestruct.r_inode.getInodeByID(fh).write(data)

        print("dirPresent"+str(self.dirPresent) +"fh  "+str(fh))
        dirPresentInode = inodestruct.r_inode.getInodeByID(self.dirPresent)
        byteName = str.encode(str(dirPresentInode.getNameByID(fh)) )

        print("dirPresentInode ******************")
        print(dirPresentInode.fileTable)
        threading.Thread(target=threadCountDown, args=(byteName,self.dirPresent,) ).start()

        return len(buf)

def threadCountDown(filename,inode_parent):
    global deley_time
    print('create thread')
    sleep(deley_time)
    print('end ')
    print(filename)

    parentArchiveInode = inodestruct.r_inode.getInodeByID(inode_parent)
    operations = Vcowfs()

    if 'archive' in parentArchiveInode.fileTable  :
         print("yes")
    else:
         print("no")
         operations.mkdir(inode_parent, b'archive' , 0)



    archiveInodeNumber = parentArchiveInode.fileTable['archive']


    dirPresentInode = inodestruct.r_inode.getInodeByID(inode_parent)
    print(dirPresentInode.fileTable)

    print("parentArchiveInode.fileTable ++++++++++")
    print(parentArchiveInode.fileTable)
    print(filename.decode("utf-8"))
    fileOriginalInodeNum = parentArchiveInode.fileTable[ filename.decode("utf-8") ]
    fileOriginalInode = inodestruct.r_inode.getInodeByID(fileOriginalInodeNum)

    #if True:
    if int(time() * 1e9) - fileOriginalInode.mtime_ns >= deley_time * 1000000000 :
         numberArchive  = fileOriginalInode.archive+1
         fileOriginalInode.archive = numberArchive

         strNameDesFile = filename.decode("utf-8")+'.'+str(numberArchive)
         byteNameDesFile = str.encode(strNameDesFile)
         ### create
         operations.create(archiveInodeNumber, byteNameDesFile , 0, 0)

         ### read
         data = operations.read(fileOriginalInodeNum, 0, len(fileOriginalInode.read() ))
         print("data----")
         print(data)

         #### write
         archiveInode = inodestruct.r_inode.getInodeByID(archiveInodeNumber)
         desFileInodeNumber = archiveInode.fileTable[ strNameDesFile ]

         operations.write(desFileInodeNumber, 0, data)


    print("finish")
    return

def init_logging(debug=False):
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
                                  '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if debug:
        handler.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

def parse_args(args):
    '''Parse command line'''

    parser = ArgumentParser()

    parser.add_argument('image', type=str,
                        help='Image file location')
    parser.add_argument('mountpoint', type=str,
                        help='Where to mount the file system')
    parser.add_argument('-t', action='', default=False,
                        help='Time of versioning')
    parser.add_argument('time', type=str,
                        help='time of versioning period')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debugging output')
    parser.add_argument('--debug-fuse', action='store_true', default=False,
                        help='Enable FUSE debugging output')

    return parser.parse_args(args)

def main():
    global deley_time
    options = parse_args(sys.argv[1:])
    init_logging(options.debug)
    print("\nMounting Image {} -to-> {} and version period is {}..\n".format(
          options.image, options.mountpoint, options.time))
    file = open(options.image, "rb")
    try:
        loaded_data = pickle.load(file)
        try:
            inodestruct.r_inode = loaded_data[0]
            pp.pprint(inodestruct.r_inode.slot)
        except:
            print("fail to load inodestruct.r_inode")
        try:
            inodestruct.datablockT  = loaded_data[1]
            pp.pprint(inodestruct.datablockT.slot)
        except:
            print("fail to load inodestruct.datablockT")
    except:
        print("empty image")
    file.close()
    deley_time = int(options.time)
    print(deley_time)
    testfs = Vcowfs()
    fuse_options = set(llfuse.default_options)
    fuse_options.add('fsname=vcowfs')
    fuse_options.discard('default_permissions')
    if options.debug_fuse:
        fuse_options.add('debug')
    llfuse.init(testfs, options.mountpoint, fuse_options)
    try:
        llfuse.main(workers=1)
    except:
        llfuse.close(unmount=False)
        raise

    file = open(options.image, "wb")
    print("Saving Complete XD XD XD XD XD XD")
    print(inodestruct.r_inode)
    print(inodestruct.datablockT)
    pickler = pickle.Pickler(file, -1)
    pickler.dump([inodestruct.r_inode, inodestruct.datablockT])
    file.close()
    llfuse.close()

if __name__ == '__main__':
    main()
