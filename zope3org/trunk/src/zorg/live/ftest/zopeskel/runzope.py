##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Script to run the Zope Application Server in the foreground.

$Id$
"""
import os
import sys

from pub.dbgpclient import brk

#SOFTWARE_HOME = r"Y:\zope\svn_zope3\src"
INSTANCE_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONFIG_FILE = os.path.join(INSTANCE_HOME, "etc", "zope.conf")


def run():
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(here)
    
    INSTANCE_HOME = here
    CONFIG_FILE = os.path.join(INSTANCE_HOME, "etc", "zope.conf")
    
    
    if sys.version_info < ( 2,3,5 ):
        print """\
        ERROR: Your python version is not supported by Zope3.
        Zope3 needs Python 2.3.5 or greater. You are running:""" + sys.version
        sys.exit(1)

    # This removes the script directory from sys.path, which we do
    # since there are no modules here.
    #
    basepath = filter(None, sys.path)

    #sys.path[:] = [os.path.join(INSTANCE_HOME, "lib", "python")] + basepath
    sys.path[:] = basepath

    from zope.app.twisted.main import main
    main(["-C", CONFIG_FILE] + sys.argv[1:])


if __name__ == '__main__':
    run()
