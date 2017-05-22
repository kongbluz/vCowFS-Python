import llfuse
import os

from time import time

class RootINode():
    def __init__(self):
        self.slot = {}
        self.count = llfuse.ROOT_INODE-1

    def addFile(self):
        self.count += 1
        count = self.count
        self.slot[count] = FileNode(count)
        return self.slot[count]

    def addDir(self, parent):
        self.count += 1
        count = self.count
        self.slot[count] = DirNode(count, parent)
        return self.slot[count]

    def delInode(self, id):
        del self.slot[id]

    def getInodeByID(self, id):
        return self.slot[id]

class Inode():
    def __init__(self, id):
        self.id = id
        self.mode = 16877
        self.gid = os.getgid()
        self.uid = os.getuid()
        self.type = None
        self.atime_ns = int(time() * 1e9)
        self.mtime_ns = int(time() * 1e9)
        self.ctime_ns = int(time() * 1e9)
        

    def pms_str(self):
        return 'rwxrwxrwx'

    def __str__(self):
        return str(self.id)

    def chmod(self, n_mode):
        self.ctime_ns = int(time() * 1e9)
        self.mode = n_mode


class FileNode(Inode):
    def __init__(self, id):
        super().__init__(id)
        self.type = 'file'
        self.data = [datablockT.addDatablock("")]
        self.mode = 33279
        self.fileTable = None
        self.size = 0

    def write(self, n_data):
        self.atime_ns = int(time() * 1e9)
        self.mtime_ns = int(time() * 1e9)
        BLOCKSIZE = 128
        for x in self.data:
            datablockT.delDatablock(x)
        self.data = []
        self.size = len(n_data)
        while len(n_data) > 0:
            print(len(n_data))
            self.data.append(datablockT.addDatablock(n_data[:BLOCKSIZE]))
            n_data = n_data[BLOCKSIZE:]

    def read(self):
        self.atime_ns = int(time() * 1e9)
        data = ""
        for i in self.data:
            data += datablockT.read(i)
        return data

    def getNlink(self):
        return 0

class DirNode(Inode):
    def __init__(self, id, parent):
        super().__init__(id)
        self.type = 'dir'
        self.fileTable = {}
        self.parent = parent
        self.node = 16877
        self.isAchive = False

    def addFile(self, name):
        f = r_inode.addFile()
        self.addInodeTable(name, f.id)
        return f

    def addDir(self, name):
        d = r_inode.addDir(self.id)
        self.addInodeTable(name, d.id)
        return d

    def rmInode(self, name):
        id = self.fileTable[name]
        r_inode.delInode(id)
        del self.fileTable[name]

    def rmInodeTable(self, name):
        del self.fileTable[name]

    def addInodeTable(self, name, id):
        self.fileTable[name] = id

    def ls(self):
        for file_row in self.fileTable:
            fid = self.fileTable[file_row]
            f = r_inode.getInodeByID(fid)
            print('{}{} {} id: {} time: {}'.format('-' if f.type == 'file' else 'd',
                                         f.pms_str(),
                                         file_row, fid, f.c_time))

    def getNlink(self):
        return len(self.fileTable)

class DataTable():
    def __init__(self):
        self.slot = {}
        self.count = -1

    def addDatablock(self, data):
        self.count += 1
        count = self.count
        self.slot[count] = str(data)
        return self.count

    def delDatablock(self, id):
        del self.slot[id]

    def read(self, id):
        return self.slot[id]

    def write(self, id, data):
        self.slot[id] = data

r_inode = RootINode()
datablockT = DataTable()
rootdir = r_inode.addDir(None)
