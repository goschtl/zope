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
"""Complete a windows release

This script does post processing of a windows release
(and preprocessing of an ununstall of a windows release).

$Id$
"""

import sys, os

mkzopeinstance_bat = r"""@echo off
"%s\python.exe" "%s\mkzopeinstance" %%*
"""

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if argv[1] != '-install':
        return

    scripts = os.path.split(argv[0])[0]
    install = os.path.split(scripts)[0]
    
    f = open(os.path.join(scripts, 'mkzopeinstance.bat'), 'w')
    f.write(mkzopeinstance_bat % (install, scripts))

if __name__ == '__main__':
    main(sys.argv)
