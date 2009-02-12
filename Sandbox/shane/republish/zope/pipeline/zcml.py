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
from zope.publisher.interfaces import IWSGIApplication
from zope.publisher.interfaces import IRequest
from zope.schema import Int
from zope.schema import TextLine

from zope.pipeline.apps.requestsetup import factoryRegistry


class IPipelineDirective(Interface):
    """Declare a list of application names in a WSGI pipeline"""

    for_ = GlobalObject(
        title=u'Request type',
        description=u'The type of request that should use this app list',
        required=True)

    names = Tokens(
        title=u'Application names',
        description=u'The list of WSGI application names to use.  '
            'The last name in the list declares a simple application; '
            'the rest declare a middleware application.',
        required=True)


class IApplicationDirective(Interface):
    """Declare a simple WSGI application for use at the end of a pipeline"""

    factory = GlobalObject(
        title=u"Application factory",
        description=u"A factory that creates the WSGI application.",
        required=True,
        )

    name = TextLine(
        title=u"Name",
        description=u"The name of the application",
        required=True,
        )

    for_ = GlobalObject(
        title=u"Request type",
        description=u"The request type that triggers use of this application",
        required=False,
        )


class IMiddlewareDirective(IApplicationDirective):
    """Declare a middleware WSGI application for use in a pipeline"""
    # same schema as IApplicationDirective
    pass


class IPipelineApplicationList(Interface):
    names = Attribute("Application names to use in a pipeline")


class PipelineApplicationList(object):
    implements(IPipelineApplicationList)

    def __init__(self, names):
        self.names = names

    def adapt(self, request):
        """Called by adapter lookup"""
        return self


def pipeline(_context, for_, names):
    """Register a pipeline application list"""
    obj = PipelineApplicationList(names)
    adapter(_context, factory=obj.adapt,
        provides=[IPipelineApplicationList], for_=[for_])

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


class IRequestFactoryDirective(Interface):
    """Link information from a request to a request factory"""

    name = TextLine(
        title=u'Name',
        description=u'The name of the request factory.')

    factory = GlobalObject(
        title=u'Factory',
        description=(u'The request factory, which is a callable '
                     u'that accepts one parameter, the WSGI environment, '
                     u'and returns a request object. '
                     u'The factory can return None to defer to the '
                     u'next registered factory.'),
        required=True)

    schemes = Tokens(
        title=u'URL Schemes',
        description=(u'A list of URL schemes to support. This matches the '
                     u'wsgi.url_scheme parameter. Defaults to "http https".'),
        value_type=TextLine(),
        required=False)

    methods = Tokens(
        title=u'Methods',
        description=(u'A list of HTTP method names. If the method is a "*", '
                     u'then all methods will match. Example: "GET POST"',
        value_type=TextLine(),
        required=False)

    mimetypes = Tokens(
        title=u'Mime Types',
        description=(u'A list of content/mime types of the request. If the '
                     u'type is a "*" then all types will be matched. '
                     u'Example: "text/html text/xml"'),
        value_type=TextLine(),
        required=False)

    priority = Int(
        title=u'Priority',
        description=(u'A priority key used to decide between coexistent'
                     ' request factories.'),
        required=False)

def request_factory(_context, name, factory,
    schemes=['http', 'https'], methods=['*'], mimetypes=['*'], priority=0):

    factory = factory()

    for scheme in schemes:
        for method in methods:
            for mimetype in mimetypes:
                _context.action(
                    discriminator = (scheme, method, mimetype, priority),
                    callable = factoryRegistry.register,
                    args = (scheme, method, mimetype, name, priority, factory)
                    )
