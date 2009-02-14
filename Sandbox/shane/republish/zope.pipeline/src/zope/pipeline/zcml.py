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

from zope.component.zcml import adapter
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.publisher.interfaces import IRequest
from zope.schema import Int
from zope.schema import TextLine

from zope.pipeline.interfaces import IPipelineApplicationList
from zope.pipeline.interfaces import IWSGIApplicationFactory
from zope.pipeline.apps.requestsetup import factoryRegistry


class IPipelineDirective(Interface):
    """Declare a list of application names in a WSGI pipeline"""

    for_ = Tokens(
        title=u'Request types',
        description=u'The request types that should use this pipeline',
        value_type=GlobalObject())

    names = Tokens(
        title=u'Application names',
        description=(
            u'The list of WSGI application names to use. '
            u'The last name in the list declares a simple application; '
            u'the rest declare a middleware application.'))

class PipelineApplicationList(object):
    implements(IPipelineApplicationList)

    def __init__(self, names):
        self.names = names

    def adapt(self, marker_request):
        """Called by adapter lookup"""
        return self

def pipeline(_context, for_, names):
    """Register a pipeline application list"""
    obj = PipelineApplicationList(names)
    adapter(_context, factory=obj.adapt,
        provides=[IPipelineApplicationList], for_=for_)



class IApplicationDirective(Interface):
    """Declare a WSGI application."""

    name = TextLine(
        title=u"Name",
        description=u"The name of the application")

    factory = GlobalObject(
        title=u"Application factory",
        description=(
            u"A factory that creates the WSGI application. "
            u"If the application is used in the pipeline as "
            u"middleware, the factory will be passed a single "
            u"positional parameter containing the next "
            u"application in the pipeline.  Other parameters "
            u"specified for the pipeline may also be passed as "
            u"keyword parameters."))

    for_ = Tokens(
        title=u'Request types',
        description=u'The request types that should use this application',
        value_type=GlobalObject(),
        required=False)

class WSGIApplicationFactory(object):
    implements(IWSGIApplicationFactory)

    def __init__(self, app_factory):
        self.app_factory = app_factory

    def adapt(self, marker_request):
        """Called by adapter lookup"""
        return self

    def create(self, app_name, pipeline_params, next_app=None):
        kw = pipeline_params.get(app_name)
        if kw is None:
            kw = {}
        if next_app is not None:
            # middleware
            app = self.app_factory(next_app, **kw)
        else:
            # final app
            app = self.app_factory(**kw)
        return app

def application(_context, factory, name, for_=()):
    """Register a WSGI application"""
    if not for_:
        for_ = [IRequest]
    factory_factory = WSGIApplicationFactory(factory)
    adapter(_context,
        factory=[factory_factory.adapt],
        provides=[IWSGIApplicationFactory],
        for_=for_, name=name)




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
                     u'The factory can return None if it decides it can '
                     u'not handle the given environment.'),
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
        description=(u'A priority number used to decide between coexistent '
                     u'request factories.  A higher priority number '
                     u'is chosen before a lower priority number.'),
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
