##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grok components"""

import sys
import os
import webob
import warnings
import fnmatch

from zope import component
from zope import interface
from zope.location import Location
from zope.pagetemplate import pagetemplate, pagetemplatefile
from zope.pagetemplate.engine import TrustedAppPT

import martian.util
from cromlech.io import IResponse
from grokcore.view import interfaces, util


class Response(webob.Response):
    interface.implements(IResponse)

    def setBody(self, value):
        if isinstance(value, unicode):
            self.unicode_body = value
        else:
            self.body = value

    def getStatus(self, as_int=True):
        """returns the status of the response
        """
        if not as_int:
            return self.status
        return self.status_int

    def redirect(self, url, status=302, trusted=False):
        """Sets the response for a redirect.
        """
        self.location = url
        self.status = status


class ViewSupport(object):
    """Mixin class providing methods and properties generally
    useful for view-ish components.
    """

    @property
    def body(self):
        """The text of the request body.
        """
        return self.request.body

    def redirect(self, url, status=302, trusted=False):
        """Redirect to `url`.

        The headers of the :attr:`response` are modified so that the
        calling browser gets a redirect status code. Please note, that
        this method returns before actually sending the response to
        the browser.

        `url` is a string that can contain anything that makes sense
        to a browser. Also relative URIs are allowed.

        `status` is a number representing the HTTP status code sent
        back. If not given or ``None``, ``302`` or ``303`` will be
        sent, depending on the HTTP protocol version in use (HTTP/1.0
        or HTTP/1.1).

        `trusted` is a boolean telling whether we're allowed to
        redirect to 'external' hosts. Normally redirects to other
        hosts than the one the request was sent to are forbidden and
        will raise a :exc:`ValueError`.
        """
        return self.response.redirect(url, status=status, trusted=trusted)

    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name.

        If no arguments given, construct URL to view itself.

        If only `obj` argument is given, construct URL to `obj`.

        If only name is given as the first argument, construct URL to
        `context/name`.

        If both object and name arguments are supplied, construct URL
        to `obj/name`.

        Optionally pass a `data` keyword argument which gets added to
        the URL as a CGI query string.

        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        return util.url(self.request, obj, name, data)


class View(Location, ViewSupport):
    interface.implements(interfaces.IGrokView)

    responseFactory = Response

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = self.responseFactory()

        self.__name__ = getattr(self, '__view_name__', None)

        if getattr(self, 'module_info', None) is not None:
            self.static = component.queryAdapter(
                self.request,
                interface.Interface,
                name=self.module_info.package_dotted_name)
        else:
            self.static = None

    def __call__(self):
        self.update()
        if self.response.getStatus() in [301, 302]:
            return None
        template = getattr(self, 'template', None)
        if template is not None:
            self.response.setBody(self._render_template())
        else:
            self.response.setBody(self.render())
        return self.response

    def _render_template(self):
        return self.template.render(self)

    def namespace(self):
        """Returns a dictionary of namespaces that the template implementation
        expects to always be available.

        This method is **not** intended to be overridden by
        application developers.
        """
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def update(self, **kwargs):
        """This method is meant to be implemented by subclasses. It
        will be called before the view's associated template is
        rendered and can be used to pre-compute values for the
        template.

        update() accepts arbitrary keyword parameters which will be
        filled in from the request (in that case they **must** be
        present in the request).
        """
        pass

    def render(self, **kwargs):
        """A view can either be rendered by an associated template, or
        it can implement this method to render itself from Python.
        This is useful if the view's output isn't XML/HTML but
        something computed in Python (plain text, PDF, etc.)

        render() can take arbitrary keyword parameters which will be
        filled in from the request (in that case they *must* be
        present in the request).
        """
        pass

    render.base_method = True

# backwards compatibility. Probably not needed by many, but just in case.
# please start using grokcore.view.View again.
CodeView = View


class BaseTemplate(object):
    """Any sort of page template"""

    interface.implements(interfaces.ITemplate)

    __grok_name__ = ''
    __grok_location__ = ''

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass


class GrokTemplate(BaseTemplate):
    """A slightly more advanced page template

    This provides most of what a page template needs and is a good base for
    writing your own page template"""

    def __init__(self, string=None, filename=None, _prefix=None):

        # __grok_module__ is needed to make defined_locally() return True for
        # inline templates
        # XXX unfortunately using caller_module means that care must be taken
        # when GrokTemplate is subclassed. You can not do a super().__init__
        # for example.
        self.__grok_module__ = martian.util.caller_module()

        if not (string is None) ^ (filename is None):
            raise AssertionError(
                "You must pass in template or filename, but not both.")

        if string:
            self.setFromString(string)
        else:
            if _prefix is None:
                module = sys.modules[self.__grok_module__]
                _prefix = os.path.dirname(module.__file__)
            self.setFromFilename(filename, _prefix)

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass

    def namespace(self, view):
        # By default use the namespaces that are defined as the
        # default by the view implementation.
        return view.namespace()


class TrustedPageTemplate(TrustedAppPT, pagetemplate.PageTemplate):
    pass


class TrustedFilePageTemplate(TrustedAppPT, pagetemplatefile.PageTemplateFile):
    pass


class PageTemplate(GrokTemplate):

    def setFromString(self, string):
        zpt = TrustedPageTemplate()
        if martian.util.not_unicode_or_ascii(string):
            raise ValueError("Invalid page template. Page templates must be "
                             "unicode or ASCII.")
        zpt.write(string)
        self._template = zpt

    def setFromFilename(self, filename, _prefix=None):
        self._template = TrustedFilePageTemplate(filename, _prefix)

    def _initFactory(self, factory):

        def _get_macros(self):
            return self.template._template.macros
        # _template.macros is a property that does template reloading in debug
        # mode.  A direct "factory.macros = macros" basically caches the
        # template.  So we use a property.
        factory.macros = property(_get_macros)

    def render(self, view):
        template = self._template
        namespace = view.namespace()
        namespace.update(template.pt_getContext())
        return template.pt_render(namespace)


class PageTemplateFile(PageTemplate):
    # For BBB

    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)


_marker = object()
