##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Script to run the ZODB Browser.

$Id$
"""

import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
ZOPE3 = os.path.join(here, "Zope3")
SOFTWARE_HOME = os.path.join(here, "src")
INSTANCE_HOME = os.path.join(here, "Zope3", "src")


def run():

    # add additional path
    basepath = filter(None, sys.path)
    sys.path[:] = [INSTANCE_HOME, SOFTWARE_HOME] + basepath

    # remove bad and duplicated paths from sys.path
    goodPath = []
    badPath = [ZOPE3, here]
    for path in sys.path:
        if path not in badPath:
            goodPath.append(path)

    sys.path[:] = goodPath

    from z3c.zodbbrowser.main import main
    main()


if __name__ == '__main__':
    run()
