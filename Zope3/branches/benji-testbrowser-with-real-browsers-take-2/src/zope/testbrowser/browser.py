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
"""Mechanize-based Functional Doctest interfaces

$Id$
"""
__docformat__ = "reStructuredText"
from zope.testbrowser import interfaces
from zope.testbrowser.forms import getControl, getForm, getAllControls, \
    controlFactory, Form
from zope.testbrowser.utilities import disambiguate, any, onlyOne, zeroOrOne, \
    SetattrErrorsMixin, PystoneTimer, compressText, RegexType
import mechanize
import re
import urllib2

try:
    from zope import interface
except ImportError:
    from dummymodules import interface

class Browser(SetattrErrorsMixin):
    """A web user agent."""
    interface.implements(interfaces.IBrowser)

    _contents = None
    _counter = 0

    def __init__(self, url=None, mech_browser=None):
        if mech_browser is None:
            mech_browser = mechanize.Browser()
        self.mech_browser = mech_browser
        self.timer = PystoneTimer()
        self._enable_setattr_errors = True

        if url is not None:
            self.open(url)

    @property
    def url(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.mech_browser.geturl()

    @property
    def isHtml(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.mech_browser.viewing_html()

    @property
    def title(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.mech_browser.title()

    @property
    def contents(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        if self._contents is not None:
            return self._contents
        response = self.mech_browser.response()
        old_location = response.tell()
        response.seek(0)
        self._contents = response.read()
        response.seek(old_location)
        return self._contents

    @property
    def headers(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.mech_browser.response().info()

    @apply
    def handleErrors():
        """See zope.testbrowser.interfaces.IBrowser"""
        header_key = 'X-zope-handle-errors'

        def get(self):
            headers = self.mech_browser.addheaders
            return dict(headers).get(header_key, True)

        def set(self, value):
            headers = self.mech_browser.addheaders
            current_value = get(self)
            if current_value == value:
                return
            if header_key in dict(headers):
                headers.remove((header_key, current_value))
            headers.append((header_key, value))

        return property(get, set)

    def open(self, url, data=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        try:
            try:
                self.mech_browser.open(url, data)
            except urllib2.HTTPError, e:
                if e.code >= 200 and e.code <= 299:
                    # 200s aren't really errors
                    pass
                else:
                    raise
        finally:
            self._stop_timer()
            self._changed()

        # if the headers don't have a status, I suppose there can't be an error
        if 'Status' in self.headers:
            code, msg = self.headers['Status'].split(' ', 1)
            code = int(code)
            if code >= 400:
                raise urllib2.HTTPError(url, code, msg, self.headers, fp=None)

    def _start_timer(self):
        self.timer.start()

    def _stop_timer(self):
        self.timer.stop()

    @property
    def lastRequestPystones(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedPystones

    @property
    def lastRequestSeconds(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedSeconds

    def reload(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.mech_browser.reload()
        self._stop_timer()
        self._changed()

    def goBack(self, count=1):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.mech_browser.back(count)
        self._stop_timer()
        self._changed()

    def addHeader(self, key, value):
        """See zope.testbrowser.interfaces.IBrowser"""
        self.mech_browser.addheaders.append( (key, value) )

    def getLink(self, text=None, url=None, id=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        if id is not None:
            def predicate(link):
                return dict(link.attrs).get('id') == id
            args = {'predicate': predicate}
        else:
            if isinstance(text, RegexType):
                text_regex = text
            elif text is not None:
                text_regex = re.compile(re.escape(text), re.DOTALL)
            else:
                text_regex = None

            if isinstance(url, RegexType):
                url_regex = url
            elif url is not None:
                url_regex = re.compile(re.escape(url), re.DOTALL)
            else:
                url_regex = None
            args = {'text_regex': text_regex, 'url_regex': url_regex}
        return Link(self.mech_browser.find_link(**args), self)

    def _clickSubmit(self, form, control, coord):
        self._start_timer()
        self.mech_browser.open(form.click(
                    id=control.id, name=control.name, coord=coord))
        self._stop_timer()

    def _changed(self):
        self._counter += 1
        self._contents = None

    def getControl(self, label=None, name=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        forms = self.mech_browser.forms()
        control, form = getControl(forms, label, name, index)
        return controlFactory(control, form, self)

    def getForm(self, id=None, name=None, action=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        form = getForm(self.mech_browser.forms(), id, name, action, index)
        return Form(self, form)


class Link(SetattrErrorsMixin):
    interface.implements(interfaces.ILink)

    def __init__(self, link, browser):
        self.mech_link = link
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._start_timer()
        self.browser.mech_browser.follow_link(self.mech_link)
        self.browser._stop_timer()
        self.browser._changed()

    @property
    def url(self):
        return self.mech_link.absolute_url

    @property
    def text(self):
        return self.mech_link.text

    @property
    def tag(self):
        return self.mech_link.tag

    @property
    def attrs(self):
        return dict(self.mech_link.attrs)

    def __repr__(self):
        return "<%s text=%r url=%r>" % (
            self.__class__.__name__, self.text, self.url)
