##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Component registration support for services

This module provides constant definitions for the three registration states,
Unregistered, Registered, and Active.

$Id: Configuration.py,v 1.2 2002/11/30 18:35:55 jim Exp $
"""
__metaclass__ = type

from Persistence import Persistent
from ConfigurationInterfaces import IConfigurationRegistry
from Zope.Schema import Text
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.Traversing import getPhysicalPathString, traverse
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Unregistered, Registered, Active
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ContextWrapper import ContextMethod

class ConfigurationStatusProperty:

    __Zope_ContextWrapper_contextful_get__ = True
    __Zope_ContextWrapper_contextful_set__ = True

    def __init__(self, service):
        self.service = service

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configuration = inst
        service = getService(configuration, self.service)
        registry = service.queryConfigurationsFor(configuration)

        if registry:

            if registry.active() == configuration:
                return Active
            if registry.registered(configuration):
                return Registered

        return Unregistered

    def __set__(self, inst, value):
        configuration = inst
        service = getService(configuration, self.service)
        registry = service.queryConfigurationsFor(configuration)

        if value == Unregistered:
            if registry:
                registry.unregister(configuration)

        else:

            if registry is None:
                registry = service.createConfigurationsFor(configuration)
            
            if value == Registered:
                if registry.active() == configuration:
                    registry.deactivate(configuration)
                else:
                    registry.register(configuration)

            elif value == Active:
                if not registry.registered(configuration):
                    registry.register(configuration)
                registry.activate(configuration)



class ConfigurationRegistry(Persistent):

    __implements__ = IConfigurationRegistry

    _data = ()

    def _id(self, ob):

        # Get and check relative path
        prefix = "/++etc++Services/Packages/"
        path = getPhysicalPathString(ob)
        lpackages = path.rfind(prefix)
        if lpackages < 0:
            raise ValueError("Configuration object is in an invalid location",
                             path)

        rpath = path[lpackages+len(prefix):]
        if not rpath or (".." in rpath.split("/")):
            raise ValueError("Configuration object is in an invalid location",
                             path)

        return rpath

    _id = ContextMethod(_id)

    def register(self, configuration):
        cid = self._id(configuration)

        if self._data:
            if cid in self._data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            self._data = (None, )

        self._data += (cid, )

    register = ContextMethod(register)

    def unregister(self, configuration):
        cid = self._id(configuration)

        data = self._data
        if data:
            if data[0] == cid:
                # It's active, we need to switch in None
                data = (None, ) + data[1:]

                # we need to notify it that it's inactive.
                configuration.deactivated()
                
            else:
                data = tuple([item for item in data if item != cid])

        # Check for empty registry
        if len(data) == 1 and data[0] is None:
            data = ()
        
        self._data = data

    unregister = ContextMethod(unregister)

    def registered(self, configuration):
        cid = self._id(configuration)
        return cid in self._data

    registered = ContextMethod(registered)

    def activate(self, configuration):
        cid = self._id(configuration)
        data = self._data
        
        if cid in data:

            if data[0] == cid:
                return # already active
            
            if data[0] is None:
                # Remove leading None marker
                data = data[1:]
            else:
                # We need to deactivate the currently active component
                sm = getServiceManager(self)
                old = traverse(sm, 'Packages/'+data[0])
                old.deactivated()
            

            self._data = (cid, ) + tuple(
                [item for item in data if item != cid]
                )

            configuration.activated()

        else:
            raise ValueError(
                "Configuration to be activated is not regsistered",
                configuration)

    activate = ContextMethod(activate)

    def deactivate(self, configuration):
        cid = self._id(configuration)

        if cid in self._data:

            if self._data[0] != cid:
                return # already inactive

            # Just stick None on the front
            self._data = (None, ) + self._data

            configuration.deactivated()

        else:
            raise ValueError(
                "Configuration to be deactivated is not regsistered",
                configuration)

    deactivate = ContextMethod(deactivate)

    def active(self):
        if self._data:
            path = self._data[0]
            if path is not None:
                # Make sure we can traverse to it.
                sm = getServiceManager(self)
                configuration = traverse(sm, 'Packages/'+path)
                return configuration
                
        return None

    active = ContextMethod(active)

    def __nonzero__(self):
        return bool(self._data)

    def info(self):
        sm = getServiceManager(self)

        result = [{'id': path,
                   'active': False,
                   'configuration': (path and traverse(sm, 'Packages/'+path))
                   }
                  for path in self._data
                  ]

        if result:
            if result[0]['configuration'] is None:
                del result[0]
            else:
                result[0]['active'] = True
        
        return result

    info = ContextMethod(info)
