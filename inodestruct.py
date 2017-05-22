import llfuse
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
        self.permission = '777'
        self.type = None
        self.c_time = int(time())

    def pms_str(self):
        return 'rwxrwxrwx'

    def __str__(self):
        return str(self.id)


class FileNode(Inode):
    def __init__(self, id):
        super().__init__(id)
        self.type = 'file'
        self.data = ''

    def write(self, data):
        self.data = data

    def read(self):
        return self.data


class DirNode(Inode):
    def __init__(self, id, parent):
        super().__init__(id)
        self.type = 'dir'
        self.fileTable = {}
        self.parent = parent

    def addFile(self, name):
        f = r_inode.addFile()
        self.fileTable[name] = f.id
        return f

    def addDir(self, name):
        d = r_inode.addDir(self.id)
        self.fileTable[name] = d.id
        return d

    def rmInode(self, name):
        id = self.fileTable[name]
        r_inode.delInode(id)
        del self.fileTable[name]

    def ls(self):
        for file_row in self.fileTable:
            fid = self.fileTable[file_row]
            f = r_inode.getInodeByID(fid)
            print('{}{} {} id: {} time: {}'.format('-' if f.type == 'file' else 'd',
                                         f.pms_str(),
                                         file_row, fid, f.c_time))

r_inode = RootINode()
rootdir = r_inode.addDir(None)
