#!/usr/bin/env python

# step-1
# will mount an FS, but useless beyond that

import fuse
import os # import os for current uid/gid
import stat # import stat, ExampleFS_Stat class, ExampleFS.getattr

fuse.fuse_python_api = ( 0, 2 )

# implement 
class ExampleFS_Stat( fuse.Stat ):
	def __init__( self ) :
		self.st_ino	= 0
		self.st_dev	= 0
		self.st_uid	= os.getuid() #get current user id
		self.st_gid	= os.getgid() #get current group id
		self.st_size	= 0  #size
		self.st_atime	= 0  #access time
		self.st_mtime	= 0  #modification time
		self.st_ctime	= 0  #change time
		# default to read only file
		self.st_mode = stat.S_IFREG | 0400 #type and permission
		self.st_nlink = 1 #2 for dirs, 1 for files (generally)

	def dir( self, mode = 0744 ):
		self.st_mode = stat.S_IFDIR | mode
		self.st_nlink = 2

class ExampleFS( fuse.Fuse ):
    def __init__( self, *args, **kw ):
        fuse.Fuse.__init__( self, *args, **kw )

	def getattr( self, path ):
		st = ExampleFS_Stat()
		if path == '/':
			st.dir()
		return st    

if __name__ == '__main__':
    examplefs = ExampleFS()
    args = examplefs.parse( errex = 1 )
    examplefs.main()