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

$Id: TabsDirective.py,v 1.2 2002/06/10 23:28:19 jim Exp $
"""

from Zope.Configuration.ConfigurationDirectiveInterfaces \
     import INonEmptyDirective

from Zope.Configuration.Action import Action

#from ComponentArchitecture import getService
from ZMIViewService import ZMIViews

class TabsDirective:

    __implements__ = INonEmptyDirective

    def __init__(self, _context, for_):
        self._for_ = _context.resolve(for_)

    def tab(self, _context, label, action, filter='python: 1'):
        return [
            Action(
               discriminator =('tab', self._for_, label),
               callable = ZMIViews.registerView,
               args = (self._for_, label, action, filter)
               )
            ]

    def __call__(self):
        return ()
