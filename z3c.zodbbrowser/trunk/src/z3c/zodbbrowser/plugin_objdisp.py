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
"""Plugin for object display (currently this is just for fun)"""

from wax import *

from z3c.zodbbrowser.bases import BaseObjDisplayPlugin


class dictDispPlugin(BaseObjDisplayPlugin):
    title = u'dict details'

    def onClick(self):
        dlg = MessageDialog(self.form, "A message", "dict details")
        dlg.ShowModal()
        dlg.Destroy()

def register(registry):
    registry['obj_display'].append(('dict', dictDispPlugin))
