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

from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.interface.implements import implements, getImplements

from zope.app.interfaces.introspector import IIntrospector
from zope.app.interfaces.services.module import IModuleService
from zope.component import getServiceManager, getAdapter, \
     queryServiceManager, getServiceDefinitions
from zope.proxy.introspection import removeAllProxies


class Introspector:
    """Introspects an object"""

    __implements__ = IIntrospector

    def __init__(self, context):
        self.context = context
        self.request = None
        self.currentclass = None

    def isInterface(self):
        "Checks if the context is class or interface"
        try:
            ck = self.context.namesAndDescriptions()
            return True
        except:
            return False

    def setRequest(self, request):
        """sets the request"""
        self.request = request
        if 'PATH_INFO' in request:
            path = self.request['PATH_INFO']
        else:
            path = ''
        name = path[path.rfind('++module++') + len('++module++'):]
        name = name.split('/')[0]
        if path.find('++module++') != -1:
            if (self.context == Interface and
                name != 'Interface._Interface.Interface'):
                servicemanager = getServiceManager(self.context)
                adapter = getAdapter(servicemanager, IModuleService)
                self.currentclass = adapter.resolve(name)
                self.context = self.currentclass
            else:
                self.currentclass = self.context
        else:
            self.currentclass = self.context.__class__

    def _unpackTuple(self, tuple_obj):
        res = []
        for item in tuple_obj:
            if type(item)==tuple:
                res.extend(self._unpackTuple(item))
            else:
                res.append(item)
        return tuple(res)

    def getClass(self):
        """Returns the class name"""
        return (self.currentclass).__name__

    def getBaseClassNames(self):
        """Returns the names of the classes"""
        bases = self.getExtends()
        base_names = []
        for base in bases:
            base_names.append(base.__module__+'.'+base.__name__)
        return base_names

    def getModule(self):
        """Returns the module name of the class"""
        return (self.currentclass).__module__

    def getDocString(self):
        """Returns the description of the class"""
        return removeAllProxies(self.currentclass).__doc__

    def getInterfaces(self):
        """Returns interfaces implemented by this class"""
        interfaces = removeAllProxies(self.currentclass).__implements__
        if type(interfaces) != tuple:
            interfaces = (interfaces,)
        else:
            interfaces = self._unpackTuple(interfaces)
        return interfaces

    def getInterfaceNames(self):
        names = []
        try:
            for intObj in self.getInterfaces():
                names.append(intObj.__module__ + '.' + intObj.__name__)
        except:
            return []
        else:
            names.sort()
            return names

    def getInterfaceDetails(self):
        """Returns the entire documentation in the interface"""
        interface = self.context
        Iname = interface.__name__
        bases = []
        desc = ''
        methods = []
        attributes = []
        if interface is not None:
            namesAndDescriptions = interface.namesAndDescriptions()
            namesAndDescriptions.sort()
            for name, desc in namesAndDescriptions:
                if hasattr(desc, 'getSignatureString'):
                    methods.append((desc.getName(),
                                    desc.getSignatureString(),
                                    desc.getDoc()))
                else:
                    attributes.append((desc.getName(), desc.getDoc()))

            for base in interface.getBases():
                bases.append(base.__module__+'.'+base.__name__)
            desc = str(interface.__doc__)
        return [Iname, bases, desc, methods, attributes]

    def getExtends(self):
        """Returns all the class extended up to the top most level"""
        bases = self._unpackTuple((self.currentclass).__bases__)
        return bases

    def getInterfaceConfiguration(self):
        """Returns details for a interface configuration"""
        #sm = queryServiceManager(self.context)
        service = []
        for name, interface in getServiceDefinitions(self.context):
            if self.context.extends(interface):
                service.append(str(name))
        print service
        return service
