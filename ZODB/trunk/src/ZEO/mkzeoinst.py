#!python
##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""mkzeoinst.py -- create a ZEO instance.

Usage: mkzeoinst.py home [port]

Given an "instance home directory" <home> and some configuration
options (all of which have default values), create the following:

<home>/etc/zeo.conf     -- ZEO config file
<home>/etc/runner.conf  -- zdctl config file
<home>/var/             -- Directory for data files: Data.fs etc.
<home>/log/             -- Directory for log files: zeo.log and runner.log
<home>/bin/zeoctl       -- start/stop script (a shim for zdctl.py)

The script will not overwrite existing files; instead, it will issue a
warning if an existing file is found that differs from the file that
would be written if it didn't exist.

The script assumes that runzeo.py, zdrun.py, and zdctl.py can be found
on the shell's $PATH, and that their #! line names the right Python
interpreter.  When you use the ZODB3 setup.py script to install the
ZODB3 software, this is taken care of.
"""

import os
import sys
import stat
import getopt

zeo_conf_template = """# ZEO configuration file

<zeo>
  address %(port)d
  read-only false
  invalidation-queue-size 100
  # monitor-address PORT
  # transaction-timeout SECONDS
</zeo>

<filestorage 1>
  path %(home)s/var/Data.fs
</filestorage>

<eventlog>
  level info
  <logfile>
    path %(home)s/log/zeo.log
  </logfile>
</eventlog>
"""

runner_conf_template = """# runner configuration file

<runner>
  program %(runzeo)s -C %(home)s/etc/zeo.conf
  socket-name %(home)s/etc/zeo.zdsock
</runner>

<eventlog>
  level info
  <logfile>
    path %(home)s/log/runner.log
  </logfile>
</eventlog>
"""

zeoctl_template = """#!/bin/sh
# ZEO instance start script
exec %(zdctl)s -C %(home)s/etc/runner.conf ${1+"$@"}
"""

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.error, msg:
        print msg
        sys.exit(2)
    if len(args) not in [1, 2]:
        print "Usage: mkzeoinst.py home [port]"
        sys.exit(2)
    home = sys.argv[1]
    if sys.argv[2:]:
        port = int(sys.argv[2])
    else:
        port = 9999
    checkport(port)
    makedir(home)
    makedir(home, "etc")
    makedir(home, "var")
    makedir(home, "log")
    makedir(home, "bin")
    makefile(zeo_conf_template, home, "etc", "zeo.conf", home=home, port=port)
    makefile(runner_conf_template, home, "etc", "runner.conf",
             home=home, runzeo=which("runzeo.py"))
    makexfile(zeoctl_template, home, "bin", "zeoctl",
              home=home, python=sys.executable, zdctl=which("zdctl.py"))
    print "All done."

def checkport(port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", port))
    except socket.error:
        print "A process is already listening on port %d" % port
        sys.exit(2)
    s.close()

def which(program):
    strpath = os.getenv("PATH")
    binpath = strpath.split(os.pathsep)
    for dir in binpath:
        path = os.path.join(dir, program)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    raise IOError, "can't find %r on path %r" % (program, strpath)

def makedir(*args):
    path = ""
    for arg in args:
        path = os.path.join(path, arg)
    mkdirs(path)
    return path

def mkdirs(path):
    if os.path.isdir(path):
        return
    head, tail = os.path.split(path)
    if head and tail and not os.path.isdir(head):
        mkdirs(head)
    os.mkdir(path)
    print "Created directory", path

def makefile(template, *args, **kwds):
    path = makedir(*args[:-1])
    path = os.path.join(path, args[-1])
    data = template % kwds
    if os.path.exists(path):
        f = open(path)
        olddata = f.read().strip()
        f.close()
        if olddata:
            if olddata != data.strip():
                print "Warning: not overwriting existing file %r" % path
            return path
    f = open(path, "w")
    f.write(data)
    f.close()
    print "Wrote file", path
    return path

def makexfile(template, *args, **kwds):
    path = makefile(template, *args, **kwds)
    umask = os.umask(022)
    os.umask(umask)
    mode = 0777 & ~umask
    if stat.S_IMODE(os.stat(path)[stat.ST_MODE]) != mode:
        os.chmod(path, mode)
        print "Changed mode for %s to %o" % (path, mode)
    return path

if __name__ == "__main__":
    main()
