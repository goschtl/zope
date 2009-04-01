##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Experimental support for browser "applications"
"""

import cgi
import logging
import simplejson
import zc.ajax.interfaces
import zc.resourcelibrary
import zope.app.exception.browser.unauthorized
import zope.app.pagetemplate
import zope.cachedescriptors.property
import zope.component
import zope.exceptions.interfaces
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser
import zope.security.proxy
import zope.traversing.interfaces

def result(data):
    if not data:
        data = dict(success=True)
    elif isinstance(data, dict) and not 'success' in data:
        data['success'] = not (('error' in data)
                                 or ('errors' in data))

    return simplejson.dumps(data)

class _method(object):

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    __Security_checker__ = zope.security.checker.NamesChecker(
        ('__call__', 'browserDefault')
        )

    def __init__(self, inst, func):
        self.im_self = inst
        self.im_func = func

    def __call__(self, *a, **k):
        return self.im_func(self.im_self, *a, **k)

    def browserDefault(self, request):
        return self, ()

class _jsonmethod(_method):

    def __call__(self, *a, **k):
        return result(self.im_func(self.im_self, *a, **k))

class page(object):

    _method_class = _method

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        if inst is None:
            return self
        return self._method_class(inst, self.func)

class jsonpage(page):
    _method_class = _jsonmethod

class AttributeTraversable(object):

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    def publishTraverse(self, request, name):
        name = name.replace('.', '_')
        result = getattr(self, name, None)
        if zope.publisher.interfaces.browser.IBrowserPublisher.providedBy(
            result):
            zope.interface.directlyProvides(
                request,
                zc.ajax.interfaces.IAjaxRequest,
                zope.interface.directlyProvidedBy(request),
                )
            return result
        raise zope.publisher.interfaces.NotFound(self, name, request)    

    @zope.cachedescriptors.property.Lazy
    def __parent__(self):
        return self.context

class PublicTraversable(object):
    
    __Security_checker__ = zope.security.checker.NamesChecker((
        'browserDefault', 'publishTraverse'))

class Trusted(object):
    
    def __init__(self, context, *a, **kw):
        context = zope.security.proxy.removeSecurityProxy(context)
        super(Trusted, self).__init__(context, *a, **kw)

class Application(AttributeTraversable):

    zope.component.adapts(
        zope.traversing.interfaces.IContainmentRoot,
        zope.publisher.interfaces.browser.IBrowserRequest,
        )
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        return self, ('index.html', )

    def template(self):
        return '<html><head></head></html>'

    @page
    def index_html(self):
        try:
            library = self.resource_library_name
        except AttributeError:
            raise AttributeError(
                "No resource_library_name attribute is defined.\n"
                "This attribute is required to specify the name of a\n"
                "library to use (need). It may be set to None to avoid\n"
                "requiring a resource library."
                )
        if library is not None:
            zc.resourcelibrary.need(library)
        return self.template()

class SubApplication(AttributeTraversable):

    def __init__(self, context, request, base_href=None):
        self.context = context
        self.request = request
        if base_href is not None:
            self.base_href = base_href
        

class traverser(object):

    def __init__(self, func, inst=None):
        self.func = func
        self.inst = inst
    
    def __get__(self, inst, cls):
        if inst is None:
            return self
        return traverser(self.func, inst)

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    __Security_checker__ = zope.security.checker.NamesChecker((
        'publishTraverse', ))

    def publishTraverse(self, request, name):
        return self.func(self.inst, request, name)

    def __call__(self, *args, **kw):
        if self.inst is None:
            return self.func(*args, **kw)
        else:
            return self.func(self.inst, *args, **kw)
            

class UserError:

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)
    zope.component.adapts(zope.exceptions.interfaces.IUserError,
                          zc.ajax.interfaces.IAjaxRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return simplejson.dumps(dict(
            success = False,
            error = str(self.context),
            ))

class ExceptionView(UserError):

    zope.component.adapts(Exception,
                          zc.ajax.interfaces.IAjaxRequest)

    def __call__(self):
        self.request.response.setStatus(500)

        logger = logging.getLogger(__name__)
        logger.exception(
            'SysError created by zc.ajax'
            )
        return simplejson.dumps(dict(
            success = False,
            error = "%s: %s" % (self.context.__class__.__name__, self.context),
            ))
