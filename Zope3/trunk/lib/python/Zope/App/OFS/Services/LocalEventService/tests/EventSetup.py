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

Revision information:
$Id: EventSetup.py,v 1.2 2002/06/10 23:28:11 jim Exp $
"""
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
  import PlacefulSetup
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable
from Zope.App.OFS.Container.ContainerTraversable import ContainerTraversable
from Zope.App.OFS.Container.IContainer import IReadContainer
from Zope.App.OFS.Services.LocalEventService.LocalEventService import LocalEventService

class EventSetup(PlacefulSetup):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        adapterService=getService(None, "Adapters")
        adapterService.provideAdapter(
            None, ITraverser, Traverser)
        adapterService.provideAdapter(
            None, ITraversable, DefaultTraversable)
        adapterService.provideAdapter(
            IReadContainer, ITraversable, ContainerTraversable)
        from Zope.Event.IEventService import IEventService
        from Zope.Event.GlobalEventService import eventService
        globsm=getServiceManager(None)
        globsm.defineService("Events", IEventService)
        globsm.provideService("Events", eventService)
        self.createEventService()
    
    def createEventService(self, folder=None):
        if folder is None: folder=self.rootFolder
        if not folder.hasServiceManager():
            self.createServiceManager(folder)
        sm=getServiceManager(folder) # wrapped now
        sm.setObject("myEventService",LocalEventService())
        sm.bindService("Events","myEventService")
        
    
