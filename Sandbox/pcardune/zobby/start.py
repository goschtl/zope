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

$Id: start.py 72 2007-03-26 15:31:12Z rineichen $
"""

import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
ZOPE3 = os.path.join(here, "Zope3")
SOFTWARE_HOME = os.path.join(here, "src")
INSTANCE_HOME = os.path.join(here, "Zope3", "src")
CONFIG_FILE = os.path.join(here, "etc", "zope.conf")


def run():
    if sys.version_info < ( 2,3,5 ):
        print """\
        ERROR: Your python version is not supported by Zope3.
        Zope3 needs Python 2.3.5 or greater. You are running:""" + sys.version
        sys.exit(1)

    # add additional path
    basepath = filter(None, sys.path)
    sys.path[:] = [INSTANCE_HOME, SOFTWARE_HOME] + basepath

    # remove bad and duplicated paths from sys.path
    goodPath = []
    badPath = [ZOPE3, here]
    for path in sys.path:
        if path not in badPath:
            goodPath.append(path)
        else:
            badPath.append(path)

    sys.path[:] = goodPath

    from zope.app.twisted.main import main
    main(["-C", CONFIG_FILE] + sys.argv[1:])


if __name__ == '__main__':
     iconf = os.path.join(here, 'etc', 'instance.conf')
     if not os.path.exists(iconf):
         print "creating local instance.conf: %s" % iconf
         f = file(iconf,'w')
         f.write("%%define INSTANCE %s" % here)
         f.close()
     run()
