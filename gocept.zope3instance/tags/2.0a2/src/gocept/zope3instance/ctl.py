##############################################################################
#
# Copyright (c) 2004-2007 Zope Corporation and Contributors.
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
"""Top-level controller for 'zopectl'.
"""

import os
import zdaemon.zdctl

class ZopectlCmd(zdaemon.zdctl.ZDCmd):

    def do_debug(self, rest):
        os.system(self._debugzope)

    def help_debug(self):
        print "debug -- Initialize the Zope application, providing a"
        print "         debugger object at an interactive Python prompt."

    def do_run(self, arg):
        os.system(self._scriptzope + ' ' + arg)

    def help_run(self):
        print "run <script> [args] -- run a Python script with the Zope "
        print "                       environment set up.  The script has "
        print "                       'root' exposed as the root container."


def main(debugzope, scriptzope, args):

    class Cmd(ZopectlCmd):
        _debugzope = debugzope
        _scriptzope = scriptzope

    zdaemon.zdctl.main(args, None, Cmd)
