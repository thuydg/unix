#!/usr/bin/env python

#    Copyright (C) 2001  Jeff Epler  <jepler@unpythonic.dhs.org>
#    Copyright (C) 2006  Csaba Henk  <csaba.henk@creo.hu>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os, sys
from errno import *
from stat import *
import fcntl

import fuse
from fuse import Fuse

import re #regular expression
import datetime

import logging
logging.basicConfig(filename='log.txt',level=logging.DEBUG)

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)
now = datetime.datetime.now()
# We use a custom file class
fuse.feature_assert('stateful_files', 'has_init')


def flag2mode(flags):
    md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m

#function to check the time to open! here to break the rule!!
def time_to_open(path):
    #create the regular expression to test if the path is need to check or not
    year_reg = '([0-9][0-9][0-9][0-9])'
    month_reg = '(1[0-2]|0[1-9])'
    day_reg = "(1[0-9]|2[0-9]|3[0-1]|0[1-9])"
    p = re.compile("/(%s%s%s)/" % (year_reg, month_reg, day_reg))
    datelist = p.findall(path)
    
    if len(datelist) == 0:
        return True

    datelist_int = map((lambda x:int(x[0])),datelist)
    date_most_future = max(datelist_int)
    now = datetime.datetime.today()
    now_int =  now.year *10000 + now.month * 100 + now.day

    return date_most_future < now_int


class Xmp(Fuse):

    def __init__(self, *args, **kw):

        Fuse.__init__(self, *args, **kw)

        # do stuff to set up your filesystem here, if you want
        #import thread
        #thread.start_new_thread(self.mythread, ())
        self.root = '/usr/local/timecapsule/'
        # self.file_class = self.XmpFile

#    def mythread(self):
#
#        """
#        The beauty of the FUSE python implementation is that with the python interp
#        running in foreground, you can have threads
#        """
#        print "mythread: started"
#        while 1:
#            time.sleep(120)
#            print "mythread: ticking"

    def getattr(self, path):
        return os.lstat("." + path)

    def readlink(self, path):
        return os.readlink("." + path)

    def readdir(self, path, offset):
        for e in os.listdir("." + path):
            yield fuse.Direntry(e)

    def unlink(self, path):
        os.unlink("." + path)

    def rmdir(self, path):
        os.rmdir("." + path)

    def symlink(self, path, path1):
        os.symlink(path, "." + path1)

    def rename(self, path, path1):
        logging.debug(now + ' rename')       
        if not time_to_open(path):
            return -EACCES
        os.rename("." + path, "." + path1)

    def link(self, path, path1):
        logging.debug(today + 'link')
        os.link("." + path, "." + path1)

    def chmod(self, path, mode):
        os.chmod("." + path, mode)

    def chown(self, path, user, group):
        os.chown("." + path, user, group)

    def truncate(self, path, len):
        f = open("." + path, "a")
        f.truncate(len)
        f.close()

    def mknod(self, path, mode, dev):
        os.mknod("." + path, mode, dev)

    def mkdir(self, path, mode):
        os.mkdir("." + path, mode)

    def utime(self, path, times):
        os.utime("." + path, times)

    def open( self, path, mode ):
        logging.debug(now + ' open')
        if (mode & os.O_WRONLY) == 0:
            if not time_to_open(path):
                return -EACCES

    def fsinit(self):
        os.chdir(self.root)

    # def read(self, path, size, offset, fh):    
    def read(self, path, length, offset):
        logging.debug(now + 'read')
        #if (mode & os.O_WRONLY) == 0:
        #    if not time_to_open(path):
        #        return -EACCES

        f = open("." + path, "r")
        f.seek(offset)
        buffer = f.read(length)
        return buffer
    
    def write(self, path, buf, offset):
        f = open("." + path, "w")
        logging.debug(now + "seek")
        f.seek(offset)
        logging.debug(now + "write")
        f.write(buf)
        return len(buf)
    #def write(self, path, buf, offset):
    
 #   def flush(path, fh=None):
 #   def release(self, flags):
   

    def release(self, flags):
        logging.debug(now + " release")       
        mode = flag2mode(flags)
        if (mode & os.O_WRONLY) != 0:
            logging.debug("write only for relase")        
        self.file.close()   

def main():

    usage = """
Userspace nullfs-alike: mirror the filesystem tree from some point on.

""" + Fuse.fusage

    server = Xmp(version="%prog " + fuse.__version__,
                 usage=usage)

    server.parser.add_option(mountopt="root", metavar="PATH", default='/',
                             help="mirror filesystem from under PATH [default: %default]")
    server.parse(values=server, errex=1)

    logging.debug(server.root)
    try:
        if server.fuse_args.mount_expected():
            os.chdir(server.root)
    except OSError:
        print >> sys.stderr, "can't enter root of underlying filesystem"
        sys.exit(1)

    server.main()


if __name__ == '__main__':
    main()