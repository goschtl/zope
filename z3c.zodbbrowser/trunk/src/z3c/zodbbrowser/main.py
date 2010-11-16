# -*- coding: UTF-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 Zope Foundation and Contributors.
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

import os
import sys
import glob
import wx

try:
    from wax import *
    from wax.tools.choicedialog import ChoiceDialog
except ImportError:
    print "You do not have `wax` installed, please download it from http://sourceforge.net/projects/waxgui"

twist_buttons = 1

from z3c.zodbbrowser import __title__
from z3c.zodbbrowser.utils import *
from z3c.zodbbrowser.registry import getSourcePlugins
from z3c.zodbbrowser.registry import getDBDisplayPlugins
from z3c.zodbbrowser.registry import installplugins
from z3c.zodbbrowser.treehandler import rootHandler, baseHandler


class ZODBFrame(MDIParentFrame):

    def Body(self):
        self.SetTitle(__title__)

        if WAX_VERSION_TUPLE < (0,3,33):
            ShowMessage(__title__,
                        "WARNING: wax version 0.3.33 required!")

        self.CreateStatusBar()
        self.SetStatusText("")

        menubar = MenuBar(self)

        menu1 = Menu(self)

        for index, (title, ext, klass) in enumerate(getSourcePlugins()):
            # XXX I'm assuming that we won't get more than 9
            # source plugins ever.
            menu1.Append("Open %s ...\tALT+%s" % (title, index+1),
                         curry(self.menuOpen, klass),
                         "Open a database from a %s" % title)

        menu1.Append("&Close", self.menuClose)
        menu1.AppendSeparator()
        menu1.Append("E&xit\tALT+X", self.menuExit, "Exit")

        menubar.Append(menu1, "&File")

        self.SetMenuBar(menubar)

    def menuOpen(self, openerklass, event=None):
        opener = openerklass(self)
        if opener.open(self):
            viewopts = opener.getSupportedDisplays()

            frameklasses = getDBDisplayPlugins(viewopts)

            klassindex = None
            if len(frameklasses) == 0:
                ShowMessage(__title__,
                    "Happens that there is no display plugin for %s" % \
                    viewopts)
            elif len(frameklasses) == 1:
                klassindex = 0
            else:
                opts = [ii.title for ii in frameklasses]
                dlg = ChoiceDialog(self,
                                   title=__title__,
                                   prompt="Choose a display method",
                                   choices=opts)
                try:
                    result = dlg.ShowModal()
                    if result == 'ok':
                        klassindex = dlg.choice
                finally:
                    dlg.Destroy()

            if klassindex is not None:
                frame = frameklasses[klassindex](parent=self,
                                                 opener = opener)
                frame.Show()

    def menuClose(self, event):
        while True:
            chld = self.GetActiveChild()
            if chld:
                chld.Close()
            else:
                break
        pass

    def menuExit(self, event):
        self.Destroy()


def main():
    installplugins()

    app = Application(ZODBFrame)
    app.MainLoop()


if __name__ == '__main__':
    main()
