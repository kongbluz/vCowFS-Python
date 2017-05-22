#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
tmpfs.py - Example file system for Python-LLFUSE.

This file system stores all data in memory. It is compatible with both Python
2.x and 3.x.

Copyright © 2013 Nikolaus Rath <Nikolaus.org>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from __future__ import division, print_function, absolute_import

import os
import sys

# We are running from the Python-LLFUSE source directory, put it
# into the Python path.
basedir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
if (os.path.exists(os.path.join(basedir, 'setup.py')) and
    os.path.exists(os.path.join(basedir, 'src', 'llfuse'))):
    sys.path.append(os.path.join(basedir, 'src'))

import llfuse
from inodestruct import *
import errno
import stat
from time import time
import sqlite3
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

rootdir.addFile('Fhheeewwwwwww')
rootdir.addFile('dummmmmmmyyyy')
rootdir.addDir('myDir')
log = logging.getLogger()

# For Python 2 + 3 compatibility
if sys.version_info[0] == 2:
    def next(it):
        return it.next()
else:
    buffer = memoryview

class Operations(llfuse.Operations):
    '''An example filesystem that stores all data in memory

    This is a very simple implementation with terrible performance.
    Don't try to store significant amounts of data. Also, there are
    some other flaws that have not been fixed to keep the code easier
    to understand:

    * atime, mtime and ctime are not updated
    * generation numbers are not supported
    '''


    def __init__(self):
        super(Operations, self).__init__()
        self.db = sqlite3.connect(':memory:')
        self.db.text_factory = str
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.inode_open_count = defaultdict(int)
        self.init_tables()

    def init_tables(self):
        log.debug("init_tables")
        '''Initialize file system tables'''

        self.cursor.execute("""
        CREATE TABLE inodes (
            id        INTEGER PRIMARY KEY,
            uid       INT NOT NULL,
            gid       INT NOT NULL,
            mode      INT NOT NULL,
            mtime_ns  INT NOT NULL,
            atime_ns  INT NOT NULL,
            ctime_ns  INT NOT NULL,
            target    BLOB(256) ,
            size      INT NOT NULL DEFAULT 0,
            rdev      INT NOT NULL DEFAULT 0,
            data      BLOB
        )
        """)

        self.cursor.execute("""
        CREATE TABLE contents (
            rowid     INTEGER PRIMARY KEY AUTOINCREMENT,
            name      BLOB(256) NOT NULL,
            inode     INT NOT NULL REFERENCES inodes(id),
            parent_inode INT NOT NULL REFERENCES inodes(id),

            UNIQUE (name, parent_inode)
        )""")

        # Insert root directory
        now_ns = int(time() * 1e9)
        self.cursor.execute("INSERT INTO inodes (id,mode,uid,gid,mtime_ns,atime_ns,ctime_ns) "
                            "VALUES (?,?,?,?,?,?,?)",
                            (llfuse.ROOT_INODE, stat.S_IFDIR | stat.S_IRUSR | stat.S_IWUSR
                              | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH
                              | stat.S_IXOTH, os.getuid(), os.getgid(), now_ns, now_ns, now_ns))
        self.cursor.execute("INSERT INTO contents (name, parent_inode, inode) VALUES (?,?,?)",
                            (b'..', llfuse.ROOT_INODE, llfuse.ROOT_INODE))


    def get_row(self, *a, **kw):
        log.debug("get_row")
        self.cursor.execute(*a, **kw)
        try:
            row = next(self.cursor)
        except StopIteration:
            raise NoSuchRowError()
        try:
            next(self.cursor)
        except StopIteration:
            pass
        else:
            raise NoUniqueValueError()
        return row

    def lookup(self, inode_p, name, ctx=None):
        log.debug("lookup ++++ named" + name.decode("utf-8") )
        log.debug(str(inode_p)  +"zzzzz")
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
            if name.decode("utf-8") not in r_inode.getInodeByID(inode_p).fileTable:
                log.debug('look up chioce : 31111111111')
                raise(llfuse.FUSEError(errno.ENOENT))
            else:
                log.debug('look up chioce : 32222222222')
                inode = r_inode.getInodeByID(inode_p).fileTable[name.decode("utf-8")]
        log.debug("inode in look up : "  + str(inode))
        return self.getattr(inode, ctx)


    def getattr(self, inode, ctx=None):
        log.debug("getattr")
        log.debug("get attr inode# : " + str(inode))
        row = r_inode.getInodeByID(inode)

        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout = 300
        # if row.type == 'file':
        #     log.debug("is file")
        #     entry.st_mode = 33279
        # else:
        #     log.debug("is dir")
        #     entry.st_mode = 16877
        entry.st_mode = row.mode
        entry.st_nlink = row.getNlink()
        entry.st_uid = row.uid
        entry.st_gid = row.gid
        entry.st_rdev = 0
        entry.st_size = 0

        entry.st_blksize = 512
        entry.st_blocks = 1
        entry.st_atime_ns = row.atime_ns
        entry.st_mtime_ns = row.mtime_ns
        entry.st_ctime_ns = row.ctime_ns

        log.debug(entry.st_mode)
        return entry

    def readlink(self, inode, ctx):
        log.debug("readlink")
        return self.get_row('SELECT * FROM inodes WHERE id=?', (inode,))['target']

    def opendir(self, inode, ctx):
        log.debug("opendir")
        return inode

    def readdir(self, inode, off):
        log.debug("readdir #" + str(inode) + " offff" + str(off))

        if off == 0:
            rootz = r_inode.getInodeByID(inode).fileTable
            parent = r_inode.getInodeByID(inode).parent
            yield  (b".", self.getattr(inode), inode)
            if parent == None:
                yield  (b"..", self.getattr(inode), inode)
            else:
                yield  (b"..", self.getattr(parent), parent)
            # yield  ("..", self.getattr(rootz[name]), rootz[name])
            for name in rootz:
                yield  ( str.encode(name), self.getattr(rootz[name]), rootz[name])

    def unlink(self, inode_p, name,ctx):
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
        if r_inode.getInodeByID(entry.st_ino).fileTable :
            log.debug("child of this is : "+str(r_inode.getInodeByID(entry.st_ino).fileTable))
            raise llfuse.FUSEError(errno.ENOTEMPTY)

        log.debug("delete from inode# : "+str(inode_p))
        log.debug("delete inode# : "+str(entry.st_ino))
        r_inode.getInodeByID(inode_p).rmInode(name = name.decode("utf-8"))

    def symlink(self, inode_p, name, target, ctx):
        log.debug("symlink")
        mode = (stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
        return self._create(inode_p, name, mode, ctx, target=target)

    def rename(self, inode_p_old, name_old, inode_p_new, name_new, ctx):
        log.debug("rename")
        entry_old = self.lookup(inode_p_old, name_old)

        try:
            entry_new = self.lookup(inode_p_new, name_new)
        except llfuse.FUSEError as exc:
            if exc.errno != errno.ENOENT:
                raise
            target_exists = False
        else:
            target_exists = True

        if target_exists:
            self._replace(inode_p_old, name_old, inode_p_new, name_new,
                          entry_old, entry_new)
        else:
            self.cursor.execute("UPDATE contents SET name=?, parent_inode=? WHERE name=? "
                                "AND parent_inode=?", (name_new, inode_p_new,
                                                       name_old, inode_p_old))

    def _replace(self, inode_p_old, name_old, inode_p_new, name_new,
                 entry_old, entry_new):
        log.debug("_replace")
        if self.get_row("SELECT COUNT(inode) FROM contents WHERE parent_inode=?",
                        (entry_new.st_ino,))[0] > 0:
            raise llfuse.FUSEError(errno.ENOTEMPTY)

        self.cursor.execute("UPDATE contents SET inode=? WHERE name=? AND parent_inode=?",
                            (entry_old.st_ino, name_new, inode_p_new))
        self.db.execute('DELETE FROM contents WHERE name=? AND parent_inode=?',
                        (name_old, inode_p_old))

        if entry_new.st_nlink == 1 and entry_new.st_ino not in self.inode_open_count:
            self.cursor.execute("DELETE FROM inodes WHERE id=?", (entry_new.st_ino,))


    def link(self, inode, new_inode_p, new_name, ctx):
        log.debug("link")
        entry_p = self.getattr(new_inode_p)
        if entry_p.st_nlink == 0:
            log.warn('Attempted to create entry %s with unlinked parent %d',
                     new_name, new_inode_p)
            raise FUSEError(errno.EINVAL)

        self.cursor.execute("INSERT INTO contents (name, inode, parent_inode) VALUES(?,?,?)",
                            (new_name, inode, new_inode_p))

        return self.getattr(inode)

    def setattr(self, inode, attr, fields, fh, ctx):
        log.debug("setattr")
        if fields.update_size:
            n = r_inode.getInodeByID(inode)
            data = n.data
            # data = self.get_row('SELECT data FROM inodes WHERE id=?', (inode,))[0]
            if data is None:
                data = b''
            if len(data) < attr.st_size:
                data = data + b'\0' * (attr.st_size - len(data))
            else:
                data = data[:attr.st_size]
            n.write(buffer(str.encode(data)))

        if fields.update_mode:
            log.debug("********** permission : " + str(attr.st_mode))
            r_inode.getInodeByID(inode).mode = attr.st_mode

        if fields.update_uid:
            r_inode.getInodeByID(inode).uid = attr.st_uid

        if fields.update_gid:
            r_inode.getInodeByID(inode).gid = attr.st_gid

        if fields.update_atime:
            r_inode.getInodeByID(inode).atime_ns = attr.st_atime_ns

        if fields.update_mtime:
            r_inode.getInodeByID(inode).st_mtime_ns = attr.mtime_ns

        return self.getattr(inode)

    def mknod(self, inode_p, name, mode, rdev, ctx):
        log.debug("mknod")
        return self._create(inode_p, name, mode, ctx, rdev=rdev)

    def mkdir(self, inode_p, name, mode, ctx):
        log.debug("mkdir")
        x = r_inode.getInodeByID(inode_p).addDir(name.decode("utf-8"))
        return self.getattr(x.id)

    def statfs(self, ctx):
        log.debug("statfs")
        stat_ = llfuse.StatvfsData()

        stat_.f_bsize = 512
        stat_.f_frsize = 512

        size = self.get_row('SELECT SUM(size) FROM inodes')[0]
        stat_.f_blocks = size // stat_.f_frsize
        stat_.f_bfree = max(size // stat_.f_frsize, 1024)
        stat_.f_bavail = stat_.f_bfree

        inodes = self.get_row('SELECT COUNT(id) FROM inodes')[0]
        stat_.f_files = inodes
        stat_.f_ffree = max(inodes , 100)
        stat_.f_favail = stat_.f_ffree

        return stat_

    def open(self, inode, flags, ctx):
        log.debug("open")
        # Yeah, unused arguments
        #pylint: disable=W0613
        #self.inode_open_count[inode] += 1

        # Use inodes as a file handles
        return inode

    def access(self, inode, mode, ctx):
        log.debug("access")
        # Yeah, could be a function and has unused arguments
        #pylint: disable=R0201,W0613
        return True

    def create(self, inode_parent, name, mode, flags, ctx):
        log.debug("create")
        #pylint: disable=W0612

        x = r_inode.getInodeByID(inode_parent).addFile(name.decode("utf-8"))
        return (x.id,self.getattr(x.id))

        #entry = self._create(inode_parent, name, mode, ctx)

        #self.inode_open_count[entry.st_ino] += 1
        #return (entry.st_ino, entry)

    def _create(self, inode_p, name, mode, ctx, rdev=0, target=None):
        log.debug("_create")
        if self.getattr(inode_p).st_nlink == 0:
            log.warn('Attempted to create entry %s with unlinked parent %d',
                     name, inode_p)
            raise FUSEError(errno.EINVAL)

        now_ns = int(time() * 1e9)
        self.cursor.execute('INSERT INTO inodes (uid, gid, mode, mtime_ns, atime_ns, '
                            'ctime_ns, target, rdev) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                            (ctx.uid, ctx.gid, mode, now_ns, now_ns, now_ns, target, rdev))

        inode = self.cursor.lastrowid
        self.db.execute("INSERT INTO contents(name, inode, parent_inode) VALUES(?,?,?)",
                        (name, inode, inode_p))
        return self.getattr(inode)

    def read(self, fh, offset, length):
        log.debug("read")
        fileInode = r_inode.getInodeByID(fh)
        data = fileInode.read()

        print("offset "+str(offset))
        print("length =="+str(length))
        print("strrrrrrrrrr ="+data)

        dataByte = str.encode(data)

        print("dataByte =")
        print(dataByte)
        returnData = dataByte[offset:offset+length]
        print("returnData =")
        print(returnData)

        return returnData



    def write(self, fh, offset, buf):
        log.debug("write")
        #data = self.get_row('SELECT data FROM inodes WHERE id=?', (fh,))[0]
        fileInode = r_inode.getInodeByID(fh)
        data = str.encode(fileInode.read())
        # data = b'test worked!'
        data = data[:offset] + buf + data[offset+len(buf):]
        dataStr = data.decode("utf-8")

        print("offset "+str(offset))
        print("buf ==")
        print(buf)
        print("strrrrrrrrrr ="+dataStr)

        fileInode.write(dataStr);
        return len(buf)



class NoUniqueValueError(Exception):
    def __str__(self):
        return 'Query generated more than 1 result row'


class NoSuchRowError(Exception):
    def __str__(self):
        return 'Query produced 0 result rows'

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

def parse_args():
    '''Parse command line'''

    parser = ArgumentParser()

    parser.add_argument('mountpoint', type=str,
                        help='Where to mount the file system')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debugging output')
    parser.add_argument('--debug-fuse', action='store_true', default=False,
                        help='Enable FUSE debugging output')

    return parser.parse_args()


if __name__ == '__main__':

    options = parse_args()
    init_logging(options.debug)
    operations = Operations()

    fuse_options = set(llfuse.default_options)
    fuse_options.add('fsname=tmpfs')
    fuse_options.discard('default_permissions')
    if options.debug_fuse:
        fuse_options.add('debug')
    llfuse.init(operations, options.mountpoint, fuse_options)

    # sqlite3 does not support multithreading
    try:
        llfuse.main(workers=1)
    except:
        llfuse.close(unmount=False)
        raise

    llfuse.close()
