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
$Id: EventSetup.py,v 1.5 2002/10/04 18:37:20 jim Exp $
"""
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
  import PlacefulSetup
from Zope.ComponentArchitecture import getService, getServiceManager

from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable


from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable


from Zope.App.OFS.Container.ContainerTraversable import ContainerTraversable
from Zope.App.OFS.Container.IContainer import ISimpleReadContainer



from Zope.App.OFS.Services.LocalEventService.LocalEventService \
     import LocalEventService
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.App.Traversing import getPhysicalPathString

class EventSetup(PlacefulSetup):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        adapterService = getService(None, "Adapters")
        adapterService.provideAdapter(
            None, ITraverser, Traverser)
        adapterService.provideAdapter(
            None, ITraversable, DefaultTraversable)
        adapterService.provideAdapter(
            ISimpleReadContainer, ITraversable, ContainerTraversable)

        adapterService.provideAdapter(
              None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        adapterService.provideAdapter(
              IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

        from Zope.App.Traversing.Namespaces import provideNamespaceHandler
        from Zope.App.Traversing.EtcNamespace import etc
        provideNamespaceHandler('etc', etc)
        
        self.createEventService()
    
    def createEventService(self, folder=None):
        if folder is None: folder=self.rootFolder
        if not folder.hasServiceManager():
            self.createServiceManager(folder)
        sm=getServiceManager(folder) # wrapped now
        sm.Packages['default'].setObject("myEventService",LocalEventService())

        path = "%s/Packages/default/myEventService" % getPhysicalPathString(sm)
        directive = ServiceDirective("Events", path)
        sm.Packages['default'].setObject("myEventServiceDir", directive)
        sm.bindService(directive)

        
    
