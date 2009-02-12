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
"""The request setup WSGI app and the registry for IRequest factories.
"""
__docformat__ = 'restructuredtext'

from zope.configuration.exceptions import ConfigurationError
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.testing import cleanup

from zope.pipeline.interfaces import IRequestFactoryRegistry


class CreateRequest(object):
    """WSGI middleware that creates a request and puts it in the environment.

    Chooses the type of request based on the content of the WSGI
    environment.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('wsgi.url_scheme', 'http').lower()
        method = environ.get('REQUEST_METHOD', 'GET').upper()
        mimetype = environ.get('CONTENT_TYPE', '')
        request = factoryRegistry.make_request(
            scheme, method, mimetype, environ)
        environ['zope.request'] = request

        if IBrowserRequest.providedBy(request):
            # only browser requests have skins
            setDefaultSkin(request)

        return self.app(environ, start_response)


class ProcessForm(object):
    """WSGI middleware that processes HTML form data.

    Requires the environment to contain a 'zope.request' that
    is an IHTTPRequest, not just an IRequest.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)
    request_type = IHTTPRequest

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']

        def to_unicode(text):
            charsets = request.charsets
            if not charsets:
                envadapter = IUserPreferredCharsets(request)
                charsets = envadapter.getPreferredCharsets() or ['utf-8']
                request.charsets = charsets

            for charset in charsets:
                try:
                    return unicode(text, charset)
                except UnicodeError:
                    pass
            raise UnicodeError(
                "Unable to decode %s using any available character set"
                % repr(text))

        parser = FormParser(environ, to_unicode=to_unicode)
        request.form = parser.parse()

        if parser.action:
            request.traversal_stack.insert(0, parser.action)

        return self.app(environ, start_response)


class RequestFactoryRegistry(object):
    """The registry implements a four stage lookup for registered factories
    that have to deal with requests::

        {scheme -> {method > { mimetype ->
            [
                {'priority' : some_int,
                 'factory' :  factory,
                 'name' : some_name }, ...
            ]
        }}}

    The `priority` is used to define a lookup-order when multiple factories
    are registered for the same scheme, method, and mime-type.
    """
    implements(IRequestFactoryRegistry)

    def __init__(self):
        self._d = {}   # {scheme->{method->{mimetype->{factories_data}}}}

    def register(self, scheme, method, mimetype, name, priority, factory):
        """Register a factory for scheme + method + mimetype """

        # initialize the three-level deep nested datastructure if necessary
        m = self._d.setdefault(scheme, {})
        m = m.setdefault(method, {})
        l = m.setdefault(mimetype, [])

        # Check if there is already a registered request factory (check by
        # name).  If yes then it will be removed and replaced by a new
        # factory.
        for pos, d in enumerate(l):
            if d['name'] == name:
                del l[pos]
                break
        # add the publisher factory + additional informations
        l.append({'name' : name, 'factory' : factory, 'priority' : priority})

        # order by descending priority
        l.sort(lambda x,y: -cmp(x['priority'], y['priority']))

        # check if the priorities are unique
        priorities = [item['priority'] for item in l]
        if len(set(priorities)) != len(l):
            raise ConfigurationError('All registered publishers for a given '
                                     'method+mimetype must have distinct '
                                     'priorities. Please check your ZCML '
                                     'configuration')

    def getFactoriesFor(self, scheme, method, mimetype):
        if ';' in mimetype:
            # `mimetype` might be something like 'text/xml; charset=utf8'. In
            # this case we are only interested in the first part.
            mimetype = mimetype.split(';', 1)[0]

        try:
            return self._d[scheme][method][mimetype.strip()]
        except KeyError:
            return None


    def make_request(self, scheme, method, mimetype, environment):
        """Get a factory given scheme+method+mimetype and an environment."""

        variations = [
            (scheme, method, mimetype),
            (scheme, method, '*'),
            (scheme, '*', '*')
            ]
        for s, m, mt in variations:
            factory_lst = self.getFactoriesFor(s, m, mt)
            if factory_lst:
                # Try to call each factory.  If the factory can't or
                # doesn't want to handle the given environment, it should
                # return None.
                for d in factory_lst:
                    factory = d['factory']
                    request = factory(environment)
                    if request is not None:
                        return request
        raise ConfigurationError('No registered request factory found '
            'for (%s/%s/%s)' % (scheme, method, mimetype))

factoryRegistry = RequestFactoryRegistry()

cleanup.addCleanUp(lambda : factoryRegistry.__init__())

