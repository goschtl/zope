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
"""Selenium-based Test Browser

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface

#class SeleniumBrowser(SetattrErrorsMixin):
#    """A web user agent."""
#    zope.interface.implements(interfaces.IBrowser)
#
#    _contents = None
#    _counter = 0
#
#    def __init__(self, url=None, mech_browser=None):
#        if mech_browser is None:
#            mech_browser = mechanize.Browser()
#        self.mech_browser = mech_browser
#        if url is not None:
#            self.open(url)
#        self.timer = PystoneTimer()
#        self._enable_setattr_errors = True
#
#    @property
#    def url(self):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        return self.mech_browser.geturl()
#
#    @property
#    def isHtml(self):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        return self.mech_browser.viewing_html()
#
#    @property
#    def title(self):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        return self.mech_browser.title()
#
#    @property
#    def contents(self):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        if self._contents is not None:
#            return self._contents
#        response = self.mech_browser.response()
#        old_location = response.tell()
#        response.seek(0)
#        for line in iter(lambda: response.readline().strip(), ''):
#            pass
#        self._contents = response.read()
#        response.seek(old_location)
#        return self._contents
#
#    @property
#    def headers(self):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        return self.mech_browser.response().info()
#
#    def open(self, url, data=None):
#        """See zope.testbrowser.interfaces.IBrowser"""
#        self._start_timer()
#        self.mech_browser.open(url, data)
#        self._stop_timer()
#        self._changed()
#
