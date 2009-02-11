##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Schema and implementation of WSGI pipeline directives

$Id: metadirectives.py 96177 2009-02-06 07:50:13Z shane $
"""
__docformat__ = 'restructuredtext'

from zope.component import getMultiAdapter
from zope.component.zcml import adapter
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens
from zope.interface import alsoProvides
from zope.interface import Attribute
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.schema import TextLine

from zope.publisher.interfaces import IWSGIApplication
from zope.publisher.interfaces import IRequest

class IApplicationListDirective(Interface):
    """Declare a list of application names in a WSGI pipeline"""

    for_ = GlobalObject(
        title=_('Request type'),
        description=_('The type of request that should use this app list'),
        required=True)

    names = Tokens(
        title=_('Application names'),
        description=_('The list of WSGI application names to use.  '
            'The last name in the list declares a simple application; '
            'the rest declare a middleware application.'),
        required=True)

class IPipelineDirective(Interface):
    """Declare a WSGI pipeline"""

    for_ = GlobalObject(
        title=_('Request type'),
        description=_('The type of request that should use this pipeline'),
        required=True)

class IApplicationDirective(Interface):
    """Declare a simple WSGI application for use at the end of a pipeline"""

    factory = GlobalObject(
        title=_("Application factory"),
        description=_("A factory that creates the WSGI application."),
        required=True,
        )

    name = TextLine(
        title=_("Name"),
        description=_("The name of the application"),
        required=True,
        )

    for_ = GlobalObject(
        title=_("Request type"),
        description=_("The type of request this application expects"),
        required=False,
        )

class IMiddlewareDirective(IApplicationDirective):
    """Declare a middleware WSGI application for use in a pipeline"""
    # same schema as IApplicationDirective
    pass

class IApplicationList(Interface):
    names = Attribute("Application names to use in a pipeline")

class ApplicationList(object):
    implements(IApplicationList)

    def __init__(self, names):
        self.names = names

    def adapt(self, request):
        """Called by adapter lookup"""
        return self

class MarkerRequest(object):
    """A marker object that claims to provide a request type.

    This is used for adapter lookup.
    """
    __slots__ = ('__provides__',)

    def __init__(self, request_type):
        directlyProvides(self, request_type)

class Pipeline(object):
    implements(IWSGIApplication)

    def __init__(self, request_type):
        self.app = None
        self.request_type = request_type

    def adapt(self, request):
        """Called by adapter lookup"""
        app = self.app
        if app is None:
            # cache the pipeline for future use
            self.app = app = self.make_app()
        return app

    def make_app(self):
        marker_req = MarkerRequest(self.request_type)
        app_list = IApplicationList(marker_req)
        names = list(app_list.names)  # make a copy
        # The last name in the list is an application.
        name = names.pop()
        app = IWSGIApplication(marker_req, name=name)
        while names:
            # The rest of the names are middleware.
            name = names.pop()
            app = getMultiAdapter(
                (app, marker_req), IWSGIApplication, name=name)
        return app

def application_list(_context, for_, names):
    """Register an application list"""
    obj = ApplicationList(names)
    adapter(_context, factory=obj.adapt, provides=[IAppList], for_=[for_])

def pipeline(_context, for_):
    """Register a pipeline"""
    obj = Pipeline(for_)
    adapter(_context, factory=obj.adapt, provides=[IWSGIApplication],
        for_=[for_], name='pipeline')

def application(_context, factory, name, for_=None):
    """Register a simple WSGI app for use at the end of pipeline"""
    if for_ is None:
        for_ = getattr(factory, 'request_type', IRequest)

    def app_factory(marker_request):
        res = factory()
        if not IWSGIApplication.providedBy(res):
            alsoProvides(res, IWSGIApplication)
        return res

    adapter(_context, factory=[app_factory], provides=[IWSGIApplication],
        for_=[for_], name=name)

def middleware(_context, factory, name, for_=None):
    """Register a middleware WSGI app for use in a pipeline"""
    if for_ is None:
        for_ = getattr(factory, 'request_type', IRequest)

    def app_factory(app, marker_request):
        res = factory(app)
        if not IWSGIApplication.providedBy(res):
            alsoProvides(res, IWSGIApplication)
        return res

    adapter(_context, factory=[app_factory], provides=[IWSGIApplication],
        for_=[IWSGIApplication, for_], name=name)
