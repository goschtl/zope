##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Browser-specific Publisher classes

Here we define the specific 'BrowserRequest' and 'BrowserResponse' class. The
big improvement of the 'BrowserRequest' to 'HTTPRequest' is that is can handle
HTML form data and convert them into a Python-native format. Even file data is
packaged into a nice, Python-friendly 'FileUpload' object.

$Id$
"""
__docformat__ = 'restructuredtext'

import re

import zope.component
from zope.interface import implements, directlyProvides
from zope.interface import directlyProvidedBy, providedBy
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.location import Location
from zope.httpform import FormParser
from zope.deferredimport import deprecatedFrom

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IDefaultSkin
from zope.publisher.interfaces.browser import IBrowserApplicationRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import ISkinChangedEvent
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.http import HTTPRequest, HTTPResponse

start_of_header_search=re.compile('(<head[^>]*>)', re.I).search
base_re_search=re.compile('(<base.*?>)',re.I).search
isRelative = re.compile("[-_.!~*a-zA-z0-9'()@&=+$,]+(/|$)").match

def is_text_html(content_type):
    return content_type.startswith('text/html')

DEFAULTABLE_METHODS = 'GET', 'POST', 'HEAD'


isCGI_NAME = {
    # These fields are placed in request.environ instead of request.form.
    'SERVER_SOFTWARE' : 1,
    'SERVER_NAME' : 1,
    'GATEWAY_INTERFACE' : 1,
    'SERVER_PROTOCOL' : 1,
    'SERVER_PORT' : 1,
    'REQUEST_METHOD' : 1,
    'PATH_INFO' : 1,
    'PATH_TRANSLATED' : 1,
    'SCRIPT_NAME' : 1,
    'QUERY_STRING' : 1,
    'REMOTE_HOST' : 1,
    'REMOTE_ADDR' : 1,
    'AUTH_TYPE' : 1,
    'REMOTE_USER' : 1,
    'REMOTE_IDENT' : 1,
    'CONTENT_TYPE' : 1,
    'CONTENT_LENGTH' : 1,
    'SERVER_URL': 1,
    }.has_key

hide_key={
    'HTTP_AUTHORIZATION':1,
    'HTTP_CGI_AUTHORIZATION': 1,
    }.has_key


class BrowserRequest(HTTPRequest):
    implements(IBrowserRequest, IBrowserApplicationRequest)

    __slots__ = (
        '__provides__', # Allow request to directly provide interfaces
        'form', # Form data
        '_charsets', # helper attribute
        '__annotations__',
        )

    # Set this to True in a subclass to redirect GET requests when the
    # effective and actual URLs differ.
    use_redirect = False

    def __init__(self, body_instream, environ, response=None):
        self.form = {}
        self._charsets = None
        super(BrowserRequest, self).__init__(body_instream, environ, response)

    def _get_charsets(self):
        charsets = self._charsets
        if charsets is None:
            envadapter = IUserPreferredCharsets(self)
            charsets = envadapter.getPreferredCharsets() or ['utf-8']
            self._charsets = charsets
        return charsets

    charsets = property(_get_charsets)

    def _createResponse(self):
        return BrowserResponse()

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        for charset in self.charsets:
            try:
                return unicode(text, charset)
            except UnicodeError:
                pass
        raise UnicodeError(
            "Unable to decode %s using any available character set"
            % repr(text))

    def processInputs(self):
        'See IPublisherRequest'
        parser = FormParser(self._environ, self._body_instream, self._decode)
        self.form = parser.parse()
        if parser.action:
            self.setPathSuffix((parser.action,))

    def traverse(self, obj):
        'See IPublisherRequest'

        ob = super(BrowserRequest, self).traverse(obj)
        method = self.method

        base_needed = 0
        if self._path_suffix:
            # We had a :method variable, so we need to set the base,
            # but we don't look for default documents any more.
            base_needed = 1
            redirect = 0
        elif method in DEFAULTABLE_METHODS:
            # We need to check for default documents
            publication = self.publication

            nsteps = 0
            ob, add_steps = publication.getDefaultTraversal(self, ob)
            while add_steps:
                nsteps += len(add_steps)
                add_steps = list(add_steps)
                add_steps.reverse()
                self.setTraversalStack(add_steps)
                ob = super(BrowserRequest, self).traverse(ob)
                ob, add_steps = publication.getDefaultTraversal(self, ob)

            if nsteps != self._endswithslash:
                base_needed = 1
                redirect = self.use_redirect and method == 'GET'


        if base_needed:
            url = self.getURL()
            response = self.response
            if redirect:
                response.redirect(url)
                return ''
            elif not response.getBase():
                response.setBase(url)

        return ob

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        d.update(self.form)
        return d.keys()


    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'
        marker = object()
        result = self.form.get(key, marker)
        if result is not marker:
            return result

        return super(BrowserRequest, self).get(key, default)


class RedirectingBrowserRequest(BrowserRequest):
    """Browser requests that redirect when the actual and effective URLs differ
    """

    use_redirect = True

class TestRequest(BrowserRequest):
    """Browser request with a constructor convenient for testing
    """

    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ is not None:
            _testEnv.update(environ)

        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            from StringIO import StringIO
            body_instream = StringIO('')

        super(TestRequest, self).__init__(body_instream, _testEnv)
        if form:
            self.form.update(form)

        # Setup locale object
        langs = BrowserLanguages(self).getPreferredLanguages()
        from zope.i18n.locales import locales
        if not langs or langs[0] == '':
            self._locale = locales.getLocale(None, None, None)
        else:
            parts = (langs[0].split('-') + [None, None])[:3]
            self._locale = locales.getLocale(*parts)

        if skin is not None:
            directlyProvides(self, skin)
        else:
            directlyProvides(self, IDefaultBrowserLayer)



class BrowserResponse(HTTPResponse):
    """Browser response
    """

    __slots__ = (
        '_base', # The base href
        )

    def _implicitResult(self, body):
        content_type = self.getHeader('content-type')
        if content_type is None:
            if isHTML(body):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            self.setHeader('x-content-type-warning', 'guessed from content')
            self.setHeader('content-type', content_type)

        body, headers = super(BrowserResponse, self)._implicitResult(body)
        body = self.__insertBase(body)
        # Update the Content-Length header to account for the inserted
        # <base> tag.
        headers = [
            (name, value) for name, value in headers
            if name != 'content-length'
            ]
        headers.append(('content-length', str(len(body))))
        return body, headers


    def __insertBase(self, body):
        # Only insert a base tag if content appears to be html.
        content_type = self.getHeader('content-type', '')
        if content_type and not is_text_html(content_type):
            return body

        if self.getBase():
            if body:
                match = start_of_header_search(body)
                if match is not None:
                    index = match.start(0) + len(match.group(0))
                    ibase = base_re_search(body)
                    if ibase is None:
                        # Make sure the base URL is not a unicode string.
                        base = str(self.getBase())
                        body = ('%s\n<base href="%s" />\n%s' %
                                (body[:index], base, body[index:]))
        return body

    def getBase(self):
        return getattr(self, '_base', '')

    def setBase(self, base):
        self._base = base

    def redirect(self, location, status=None):
        base = getattr(self, '_base', '')
        if base and isRelative(str(location)):
            l = base.rfind('/')
            if l >= 0:
                base = base[:l+1]
            else:
                base += '/'
            location = base + location

        # TODO: HTTP redirects must provide an absolute location, see
        #       http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.30
        #       So, what if location is relative and base is unknown?  Uncomment
        #       the following and you'll see that it actually happens.
        #
        # if isRelative(str(location)):
        #     raise AssertionError('Cannot determine absolute location')

        return super(BrowserResponse, self).redirect(location, status)

    def reset(self):
        super(BrowserResponse, self).reset()
        self._base = ''

def isHTML(str):
     """Try to determine whether str is HTML or not."""
     s = str.lstrip().lower()
     if s.startswith('<!doctype html'):
         return True
     if s.startswith('<html') and (s[5:6] in ' >'):
         return True
     if s.startswith('<!--'):
         idx = s.find('<html')
         return idx > 0 and (s[idx+5:idx+6] in ' >')
     else:
         return False

def normalize_lang(lang):
    lang = lang.strip().lower()
    lang = lang.replace('_', '-')
    lang = lang.replace(' ', '')
    return lang

class BrowserLanguages(object):
    zope.component.adapts(IHTTPRequest)
    implements(IUserPreferredLanguages)

    def __init__(self, request):
        self.request = request

    def getPreferredLanguages(self):
        '''See interface IUserPreferredLanguages'''
        accept_langs = self.request.get('HTTP_ACCEPT_LANGUAGE', '').split(',')

        # Normalize lang strings
        accept_langs = [normalize_lang(l) for l in accept_langs]
        # Then filter out empty ones
        accept_langs = [l for l in accept_langs if l]

        accepts = []
        for index, lang in enumerate(accept_langs):
            l = lang.split(';', 2)

            # If not supplied, quality defaults to 1...
            quality = 1.0

            if len(l) == 2:
                q = l[1]
                if q.startswith('q='):
                    q = q.split('=', 2)[1]
                    try:
                        quality = float(q)
                    except ValueError:
                        # malformed quality value, skip it.
                        continue

            if quality == 1.0:
                # ... but we use 1.9 - 0.001 * position to
                # keep the ordering between all items with
                # 1.0 quality, which may include items with no quality
                # defined, and items with quality defined as 1.
                quality = 1.9 - (0.001 * index)

            accepts.append((quality, l[0]))

        # Filter langs with q=0, which means
        # unwanted lang according to the spec
        # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
        accepts = [acc for acc in accepts if acc[0]]

        accepts.sort()
        accepts.reverse()

        return [lang for quality, lang in accepts]

class BrowserView(Location):
    """Browser View.

    >>> view = BrowserView("context", "request")
    >>> view.context
    'context'
    >>> view.request
    'request'

    >>> view.__parent__
    'context'
    >>> view.__parent__ = "parent"
    >>> view.__parent__
    'parent'
    """
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getParent(self):
        return getattr(self, '_parent', self.context)

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)

class BrowserPage(BrowserView):
    """Browser page

    To create a page, which is an object that is published as a page,
    you need to provide an object that:

    - has a __call__ method and that

    - provides IBrowserPublisher, and

    - if ZPT is going to be used, then your object should also provide
      request and context attributes.

    The BrowserPage base class provides a standard constructor and a
    simple implementation of IBrowserPublisher:

      >>> class MyPage(BrowserPage):
      ...     pass

      >>> request = TestRequest()
      >>> context = object()
      >>> page = MyPage(context, request)

      >>> from zope.publisher.interfaces.browser import IBrowserPublisher
      >>> IBrowserPublisher.providedBy(page)
      True

      >>> page.browserDefault(request) == (page, ())
      True

      >>> page.publishTraverse(request, 'bob') # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      NotFound: Object: <zope.publisher.browser.MyPage object at ...>, name: 'bob'

      >>> page.request is request
      True

      >>> page.context is context
      True

    But it doesn't supply a __call__ method:

      >>> page()
      Traceback (most recent call last):
        ...
      NotImplementedError: Subclasses should override __call__ to provide a response body

    It is the subclass' responsibility to do that.

    """
    implements(IBrowserPage)

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *args, **kw):
        raise NotImplementedError("Subclasses should override __call__ to "
                                  "provide a response body")

def setDefaultSkin(request):
    """Sets the default skin for the request.

    The default skin is a marker interface that can be registered as an
    adapter that provides IDefaultSkin for the request type.

    If a default skin is not available, the default layer
    (IDefaultBrowserLayer) is used.

    To illustrate, we'll first use setDefaultSkin without a registered
    IDefaultSkin adapter:

      >>> class Request(object):
      ...     implements(IBrowserRequest)

      >>> request = Request()
      >>> IDefaultBrowserLayer.providedBy(request)
      False

      >>> setDefaultSkin(request)
      >>> IDefaultBrowserLayer.providedBy(request)
      True

    When we register a default layer, however:

      >>> from zope.interface import Interface
      >>> class IMySkin(Interface):
      ...     pass
      >>> zope.component.provideAdapter(IMySkin, (IBrowserRequest,),
      ...                               IDefaultSkin)

    setDefaultSkin uses the layer instead of IDefaultBrowserLayer.providedBy:

      >>> request = Request()
      >>> IMySkin.providedBy(request)
      False
      >>> IDefaultSkin.providedBy(request)
      False

      >>> setDefaultSkin(request)

      >>> IMySkin.providedBy(request)
      True
      >>> IDefaultBrowserLayer.providedBy(request)
      False

    Any interfaces that are directly provided by the request coming into this
    method are replaced by the applied layer/skin interface:

      >>> request = Request()
      >>> class IFoo(Interface):
      ...     pass
      >>> directlyProvides(request, IFoo)
      >>> IFoo.providedBy(request)
      True
      >>> setDefaultSkin(request)
      >>> IFoo.providedBy(request)
      False

    """
    adapters = zope.component.getSiteManager().adapters
    skin = adapters.lookup((providedBy(request),), IDefaultSkin, '')
    if skin is not None:
        directlyProvides(request, skin)
    else:
        directlyProvides(request, IDefaultBrowserLayer)

def applySkin(request, skin):
    """Change the presentation skin for this request.

    >>> import pprint
    >>> from zope.interface import Interface
    >>> class SkinA(Interface): pass
    >>> directlyProvides(SkinA, IBrowserSkinType)
    >>> class SkinB(Interface): pass
    >>> directlyProvides(SkinB, IBrowserSkinType)
    >>> class IRequest(Interface): pass

    >>> class Request(object):
    ...     implements(IRequest)

    >>> req = Request()

    >>> applySkin(req, SkinA)
    >>> pprint.pprint(list(providedBy(req).interfaces()))
    [<InterfaceClass zope.publisher.browser.SkinA>,
     <InterfaceClass zope.publisher.browser.IRequest>]

    >>> applySkin(req, SkinB)
    >>> pprint.pprint(list(providedBy(req).interfaces()))
    [<InterfaceClass zope.publisher.browser.SkinB>,
     <InterfaceClass zope.publisher.browser.IRequest>]

    Changing the skin on a request triggers the ISkinChanged event:

    >>> import zope.component
    >>> from zope.publisher.interfaces.browser import ISkinChangedEvent
    >>> def receiveSkinEvent(event):
    ...     print event.request
    >>> zope.component.provideHandler(receiveSkinEvent, (ISkinChangedEvent,))
    >>> applySkin(req, SkinA)   # doctest: +ELLIPSIS
    <zope.publisher.browser.Request object at 0x...>

    Make sure our registrations go away again.

    >>> from zope.testing.cleanup import cleanUp
    >>> cleanUp()

    """
    # Remove all existing skin declarations (commonly the default skin).
    ifaces = [iface for iface in directlyProvidedBy(request)
              if not IBrowserSkinType.providedBy(iface)]
    # Add the new skin.
    ifaces.append(skin)
    directlyProvides(request, *ifaces)
    zope.event.notify(SkinChangedEvent(request))

class SkinChangedEvent(object):

    zope.interface.implements(ISkinChangedEvent)

    def __init__(self, request):
        self.request = request


deprecatedFrom(
    'This name has moved to zope.httpform.typeconv.'
    'zope.httpform.typeconv',
    'field2string', 'field2text', 'field2required', 'field2int',
    'field2float', 'field2long', 'field2tokens', 'field2lines',
    'field2boolean', 'type_converters', 'get_converter',
    'registerTypeConverter')

deprecatedFrom(
    'This name has moved to zope.httpform.parser.'
    'zope.httpform.parser',
    'Record', 'FileUpload')
