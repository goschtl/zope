##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Content component for the resource container.

$Id$
"""
__docformat__ = "reStructuredText"
import posixpath

from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from interfaces import IResourceContainer
from zope.schema.fieldproperty import FieldProperty
import zope.security.checker
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import interfaces
from zope.app.publisher.browser.fileresource import FileResource
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.datetimeutils import rfc1123_date
from zope.app.datetimeutils import time as timeFromDateTimeString
from zope.app.publisher.browser.resource import Resource
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import provideAdapter
from zope.security.checker import NamesChecker
from zope.interface import Interface
import zope.app.component.interfaces.registration
from zope.app import zapi
_marker = object()

class ResourceContainer(BTreeContainer):
    """A content type for holding resources.
    """
    implements(IResourceContainer)
    name = FieldProperty(interfaces.IResourceContainer['name'])

    def __init__(self, name,
                 layers=(IDefaultBrowserLayer,),
                 permission=zope.security.checker.CheckerPublic):
        super(ResourceContainer,self).__init__()
        self.name = name
        self.layers = layers
        self.permission = permission

def registerResourceDirectory(container):
    factory = DirectoryResourceFactory(container)
    provideAdapter(factory,self.layers,Interface,name=self.name)
    
class ResourceDirectoryRegistration(
    zope.app.component.site.AdapterRegistration):

    provided = zope.interface.Interface
    with=()
    
    def __init__(self, container):
        self.container = container

    @property
    def name(self):
        return self.container.name

    @property
    def required(self):
        return self.container.layers[0]
    
    @property
    def component(self):
        factory =  DirectoryResourceFactory(self.container)
        return factory
    


class DirectoryResource(Resource):

    implements(IBrowserPublisher)

    def __init__(self, container, request,checker):
        
        self.__container = container
        self.__checker = checker
        self.request = request
        self.__name__ = self.__container.__name__

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        return self.get(name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        res = self.get(name, None)
        if res is None:
            raise KeyError(name)
        return res

    def get(self, name, default=_marker):
        rname = posixpath.join(self.__name__, name)
        resource = ResourceFactory(name,
            self.__container,
            self.__checker,rname)(self.request)
        resource.__parent__ = self
        return resource


class DirectoryResourceFactory(object):

    def __init__(self, container):
        self.__container = container
        self.__checker = NamesChecker(
            allowed_names + ('__getitem__', 'get'),container.permission)

    def __call__(self, request):
        resource = DirectoryResource(self.__container, request, self.__checker)
        return resource


class ZODBFileResource(FileResource):

    implements(IBrowserPublisher)

    def __init__(self,context,request):
        self.context=context
        self.request=request

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return getattr(self, request.method), ()

    def _setHeaders(self):
        #XXX maybe set expires etc. headers
        response = self.request.response
        lastModified = IZopeDublinCore(self.context).modified
        lmh = rfc1123_date(self.lmt)
        response.setHeader('Content-Type', self.context.contentType)
        response.setHeader('Last-Modified', lmh)
        
    def HEAD(self):
        self._setHeaders()
        return ''

    def GET(self):
        """Default document"""
        self._setHeaders()
        return self.context.data
    

class ResourceFactory(object):

    def __init__(self, name, container, checker, path):
        self.__file = container[name]
        self.__checker = checker
        self.__name = path

    def __call__(self, request):
        resource = ZODBFileResource(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


def registerResourceDirectory(container):
    package = zapi.getParent(container)
    reg = ResourceDirectoryRegistration(container)
    package.registrationManager.addRegistration(reg)
    reg.status = zope.app.component.interfaces.registration.ActiveStatus

def reregisterResourceDirectory(container):
    registered = IRegistered(container)
    for reg in registered.registrations():
        reg.status = zope.app.component.interfaces.registration.InactiveStatus
        reg.status = zope.app.component.interfaces.registration.ActiveStatus
        

def handleResourceDirectoryModification(event, container):
    reregisterResourceDirectory(container)
