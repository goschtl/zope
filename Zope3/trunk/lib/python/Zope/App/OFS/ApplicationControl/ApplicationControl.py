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

$Id: ApplicationControl.py,v 1.4 2002/12/20 23:15:03 jim Exp $"""

from IApplicationControl import IApplicationControl
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.Security.Checker import ProxyFactory, NamesChecker

import time

class ApplicationControl:
    """ """

    __implements__ = IApplicationControl

    def __init__(self):
        self.start_time = time.time()

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.ApplicationControl.IApplicationControl.

    def getStartTime(self):
        'See Zope.App.OFS.ApplicationControl.IApplicationControl.IApplicationControl'
        return self.start_time

    #
    ############################################################

applicationController = ApplicationControl()
applicationControllerRoot = ProxyFactory(RootFolder(),
                                         NamesChecker("__class__"))
