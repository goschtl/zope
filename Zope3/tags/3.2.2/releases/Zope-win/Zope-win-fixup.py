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
"""distutils --install-script for the Windows installer.

The path to this script is passed at build-the-Windows-installer time to
setup.py as the value of the --install-script option.  The installer created
by distutils then runs this script after installation, and before
uninstallation.

At present, it does this:

Install:

  - creates mkzopeinstance.bat in Python's Scripts directory

Uninstall:

  - does nothing

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
