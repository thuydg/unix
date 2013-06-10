#!/usr/bin/env python

# step-1
# will mount an FS, but useless beyond that

import errno
import time
import fuse
import os # import os for current uid/gid
import stat # import stat, ExampleFS_Stat class, ExampleFS.getattr

fuse.fuse_python_api = ( 0, 2 )

test_file_path = '/test.txt'
test_file = 'This is a test\n by Duong'

# implement 
class ExampleFS_Stat( fuse.Stat ):
    def __init__( self ) :
        self.st_ino	= 0
        self.st_dev	= 0
        self.st_uid	= os.getuid() #get current user id
        self.st_gid	= os.getgid() #get current group id
        self.st_size	= 0  #size
        self.st_atime	= time.time()  #access time
        self.st_mtime	= time.time()  #modification time
        self.st_ctime	= time.time()  #change time
        # default to read only file
        self.st_mode = stat.S_IFREG | 0400 #type and permission
        self.st_nlink = 1 #2 for dirs, 1 for files (generally)

    def dir( self, mode = 0744 ):
        self.st_mode = stat.S_IFDIR | mode
        self.st_nlink = 2

class ExampleFS( fuse.Fuse ):
    def __init__( self, *args, **kw ):
        fuse.Fuse.__init__( self, *args, **kw )

    #get the metadata
    def getattr( self, path ):

        st = ExampleFS_Stat()

        if path == '/':
            st.dir()
            return st

        if path == test_file_path:
            st.st_size = len( test_file )
            st.st_mode = stat.S_IFREG | 0644
            return st

        if path == '/readme.txt':
            st.st_size = 512 * ( 2 ** 40 )	# hard code file size #increase size of file
            return st

        # if we are still here then this file doesn't exist
        return -errno.ENOENT

    def open( self, path, flags ):
        if path == test_file_path:
            return 0
        return -errno.ENOENT

    def read( self, path, size, offset ):
        if path != test_file_path:
            return -errno.ENOENT
        buffer = ''
        str_len = len( test_file )
        if offset < str_len:
            if offset + size > str_len:
                size = str_len - offset
            buffer = test_file[offset : offset + size]
        return buffer

    def readdir( self, path, offset ):    #??
        if path == '/':
            yield fuse.Direntry( '.' )
            yield fuse.Direntry( '..' )
            yield fuse.Direntry( 'readme.txt' )
            yield fuse.Direntry( test_file_path[1:] )

    def write( self, path, buffer, offset ):   # dont understand much
        global test_file	# force correct context
        if path != test_file_path:
            return -errno.ENOENT
        length = len( buffer )
        new_str = test_file[:offset] + buffer
        new_str += test_file[offset + length:]
        test_file = new_str
        return length

if __name__ == '__main__':
    examplefs = ExampleFS()
    args = examplefs.parse( errex = 1 )
    examplefs.main()