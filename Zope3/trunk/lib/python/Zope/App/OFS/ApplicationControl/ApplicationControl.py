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
__doc__ = """ Application Control

$Id: ApplicationControl.py,v 1.3 2002/12/20 19:45:44 jim Exp $"""

from IApplicationControl import IApplicationControl
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.Security.Checker import ProxyFactory, NamesChecker

import time

class ApplicationControl:
    """ """

    __implements__ = IApplicationControl

    def __init__(self):
        self.start_time = time.time()
        self._views = []

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.ApplicationControl.IApplicationControl.

    def getStartTime(self):
        'See Zope.App.OFS.ApplicationControl.IApplicationControl.IApplicationControl'
        return self.start_time

    def registerView(self, name, title):
        'See Zope.App.OFS.ApplicationControl.IApplicationControl.IApplicationControl'
        self._views.append({'name': name, 'title': title})

    def getListOfViews(self):
        'See Zope.App.OFS.ApplicationControl.IApplicationControl.IApplicationControl'
        return tuple(self._views)

    #
    ############################################################

applicationController = ApplicationControl()
applicationControllerRoot = ProxyFactory(RootFolder(),
                                         NamesChecker("__class__"))
