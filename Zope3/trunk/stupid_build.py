##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
Really stupid in-place builder for C extensions that are linked in to Zope 3.

usage:

$ cd /path/to/Zope3root
$ python2.2 stupid_build.py

Usage with a specific compiler such as mingw32:

$ python2.2 stupid_build.py -c mingw32
"""

import sys, os
if not (sys.version >= "2.2" and sys.version_info >= (2, 2, 2)):
    raise RuntimeError, "Python 2.2.2 or later is required"

def remove_stale_bytecode(arg, dirname, names):
    names = map(os.path.normcase, names)
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print "Removing stale bytecode file", fullname
                os.unlink(fullname)

def visit(setup_dirs, dirname, names):
    remove_stale_bytecode(None, dirname, names)
    if 'setup.py' in names:
        setup_dirs.append(dirname)

def main():
    if (not os.path.exists('products.zcml') and
        os.path.exists('products.zcml.in')):
        print 'Copying products.zcml.in to products.zcml'
        open('products.zcml', 'w').write(open('products.zcml.in').read())
    setup_dirs = []
    os.path.walk(os.getcwd(), visit, setup_dirs)
    args = tuple(sys.argv[1:])
    if not args:
        args = ('clean',)
    try:
        __file__
    except NameError:
        includes = os.path.dirname(sys.argv[0])
    else:
        includes = os.path.dirname(__file__)
    includes = os.path.join(os.path.abspath(includes), "include")
    for dir in setup_dirs:
        print "Building extensions in %s" % dir
        os.chdir(dir)
        os.spawnl(os.P_WAIT, sys.executable,
                  sys.executable, "setup.py", 'build_ext', '-i',
                  '-I', includes, *args)
        print

if __name__ == "__main__":
    main()
