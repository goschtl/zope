##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser view for the LocalInterfaceService."""

from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField
from zope.app.interfaces.services.interface import IInterfaceBasedRegistry
from zope.app import zapi

class Interfaces:
    """Interface service view

    >>> class DCInterface:
    ...     '''DCInterfaceDoc
    ...
    ...     This is a multi-line doc string.
    ...     '''
    ... 
    >>> class DummyInterface:
    ...     def items(self):
    ...         return [('DCInterface', DCInterface)]
    ...
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> interface_view = Interfaces(DummyInterface(), request)
    >>> interface_view.getInterfaces()
    [{'doc': 'DCInterfaceDoc', 'id': 'DCInterface', 'name': 'DCInterface'}]
    
    
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getInterfaces(self):
        L = [(iface.__name__, id, iface.__doc__.split('\n')[0].strip())
             for id, iface in self.context.items()]
        L.sort()
        return [{"id": id, "name": name, "doc": doc} for name, id, doc in L]

class Detail:
    """Interface Details
    
    >>> from zope.schema import TextLine
    >>> from zope.interface import Interface
    >>> from zope.i18n import MessageIDFactory
    >>> _ = MessageIDFactory('zope')
    >>> class TestInterface(Interface):
    ...     '''Test Interface'''
    ...     test_field = TextLine(title = _(u'Test Name'))
    ...     def testMethod():
    ...         'Returns test name'
    ...
    >>> class TestClass:
    ...     def getInterface(self, id=None):
    ...         return TestInterface
    ...
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = {'id': 'TestInterface'}
    >>> request.form = form
    >>> interface_details = Detail(TestClass(), request)
    >>> interface_details.setup()
    >>> interface_details.name
    'TestInterface'
    >>> interface_details.doc
    'Test Interface'
    >>> interface_details.iface.__name__
    'TestInterface'
    >>> [method['method'].__name__ for method in
    ...     interface_details.methods]
    ['testMethod']
    >>> [field.__name__ for field in interface_details.schema]
    ['test_field']

    
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def setup(self):
        try:
            id = self.request["id"]
        except KeyError:
            raise zapi.UserError("Please click on an interface name to view"
                  " details.")
        iface = self.context.getInterface(id)

        from zope.proxy import getProxiedObject
        self.iface = getProxiedObject(iface)
        
        self.name = self.iface.getName()
        # XXX the doc string needs some formatting for presentation
        # XXX self.doc = self.iface.__doc__
        self.doc = self.iface.getDoc()
        self.methods = []
        self.schema = []

        for name in self.iface:
            defn = self.iface[name]
            if IMethod.isImplementedBy(defn):
                title = defn.__doc__.split('\n')[0].strip()
                self.methods.append({'method': defn, 'title': title})
            elif IField.isImplementedBy(defn):
                self.schema.append(defn)

    def getServices(self):
        """Return an iterable of service dicts

        where the service dicts contains keys "name" and "registrations."
        registrations is a list of IRegistrations.
        """
        sm = zapi.getServiceManager(self.context)
        for name, iface in sm.getServiceDefinitions():
            service = sm.queryService(name)
            if service is None:
                continue
            registry = zapi.queryAdapter(service, IInterfaceBasedRegistry)
            if registry is None:
                continue
            regs = list(registry.getRegistrationsForInterface(self.iface))
            if regs:
                yield {"name": name, "registrations": regs}
            

class MethodDetail:
    """Interface Method Details

    >>> from zope.interface import Interface
    >>> from zope.i18n import MessageIDFactory
    >>> _ = MessageIDFactory('zope')
    >>> class TestInterface(Interface):
    ...     '''Test Interface'''
    ...     def testMethod():
    ...         'Returns test name'
    ...
    >>> class TestClass:
    ...     def getInterface(self, id=None):
    ...         return TestInterface
    ...
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = {'interface_id': 'TestInterface', 'method_id': 'testMethod'}
    >>> request.form = form
    >>> imethod_details = MethodDetail(TestClass(), request)
    >>> imethod_details.setup()
    >>> imethod_details.name
    'testMethod'
    >>> imethod_details.doc
    'Returns test name'
    >>> imethod_details.iface.__name__
    'TestInterface'
    >>> imethod_details.method.__name__
    'testMethod'

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def setup(self):
        try:
            interface_id = self.request["interface_id"]
        except KeyError:
            raise zapi.UserError("Please click on a method name in the Detail"
                                 " tab to view method details.")
        try:
            method_id = self.request["method_id"]
        except KeyError:
            raise zapi.UserError("Please click on a method name to view"
                  " details.")
        
        iface = self.context.getInterface(interface_id)

        from zope.proxy import getProxiedObject
        self.iface = getProxiedObject(iface)

        self.method = self.iface[method_id]
        self.name = self.method.__name__
        self.doc = self.method.__doc__

