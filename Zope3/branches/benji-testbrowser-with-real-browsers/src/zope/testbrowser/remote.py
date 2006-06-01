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
"""Browser-based Functional Doctests

$Id$
"""
__docformat__ = "reStructuredText"
from BeautifulSoup import BeautifulSoup
from zope.testbrowser import interfaces
from zope.testbrowser.remoteproxy2 import ServerManager, PROXY_PORT
from zope.testbrowser.utilities import disambiguate, zeroOrOne, \
    SetattrErrorsMixin, PystoneTimer
import re
import urlparse


try:
    from zope import interface
except ImportError:
    from dummymodules import interface

def getTagText(soup):
    text = str(soup)
    text = re.sub('<[^>]*>', '', text)
    text = re.sub(' +', ' ', text)
    return text

class Browser(SetattrErrorsMixin):
    """A web user agent."""
    interface.implements(interfaces.IBrowser)

    _contents = None
    _counter = 0

    def __init__(self, url=None):
        self.serverManager = ServerManager()
        self.serverManager.start()
        self.timer = PystoneTimer()
        self._enable_setattr_errors = True

        if url is not None:
            self.open(url)

    def close(self):
        self.serverManager.stop()

    @property
    def url(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.executeCommand('getUrl')

    @property
    def isHtml(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    @property
    def title(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    @property
    def contents(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        # XXX see note in commands.js
        return self.executeCommand('getContents')

    @property
    def headers(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    def handleErrors():
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    def open(self, url, data=None):
        """See zope.testbrowser.interfaces.IBrowser"""

        (scheme, netloc, path, params, query, frag) = urlparse.urlparse(url)

        if scheme != 'http':
            self.send_error(400, "unknown scheme %r" % scheme)

        url = urlparse.urlunparse(
            (scheme, '192.168.0.113:%s' % PROXY_PORT, path, params, query, frag))

        self._start_timer()
        self.executeCommand('open', url, data)
        self._stop_timer()
        self._changed()

    def executeCommand(self, command, *args):
        """Execute a JavaScript routine on the client (not an official API)"""
        return self.serverManager.executeCommand(command, *args)

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
        self.executeCommand('reload')
        self._stop_timer()
        self._changed()

    def goBack(self, count=1):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.executeCommand('goBack')
        self._stop_timer()
        self._changed()

    def addHeader(self, key, value):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    def getLink(self, text=None, url=None, id=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        soup = BeautifulSoup(self.contents)('a')
        links = []

        # "msg" holds the disambiguation message
        # the Link instance below needs to know the index of the a tag (n)
        if text is not None:
            msg = 'text %r' % text
            links = []
            for n, a in enumerate(soup):
                # remove all tags from the text in order to search it
                if text in getTagText(a):
                    links.append((a, n))
        elif url is not None:
            msg = 'url %r' % text
            for n, a in enumerate(soup):
                if a['href'] == url:
                    links.append((a, n))
        elif id is not None:
            msg = 'id %r' % id
            for n, a in enumerate(soup):
                if a['id'] == id:
                    links.append((a, n))

        link, n = disambiguate(links, msg, index)
        return Link(link, n, self)

    def getControl(self, label=None, name=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    def getForm(self, id=None, name=None, action=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        raise NotImplemented

    def _changed(self):
        self._counter += 1
        self._contents = None


class Link(SetattrErrorsMixin):
    interface.implements(interfaces.ILink)

    def __init__(self, link, index, browser):
        self.link = link
        self.browser = browser
        self.url = urlparse.urljoin(self.browser.url, link['href'])
        self._remembered_id = browser.executeCommand('rememberLinkN', index)
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._start_timer()
        self.browser.executeCommand('clickRememberedLink', self._remembered_id)
        self.browser._stop_timer()
        self.browser._changed()

    @property
    def text(self):
        return getTagText(self.link)

    @property
    def tag(self):
        return self.link.name

    @property
    def attrs(self):
        return dict(self.link.attrs)

    def __repr__(self):
        return "<%s text=%r url=%r>" % (
            self.__class__.__name__, self.text, self.url)
