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
"""Test Browser implementation that works with the Tutorial Runner

$Id$
"""
__docformat__ = "reStructuredText"

import time
import zope.interface
from zope import testbrowser


class Browser(testbrowser.browser.SetattrErrorsMixin):
    """ """
    zope.interface.implements(testbrowser.interfaces.IBrowser)

    _contents = None
    _counter = 0

    def __init__(self, broker, url=None):
        self.broker = broker
        self.timer = testbrowser.browser.PystoneTimer()
        if url:
            self.open(url)

    @property
    def url(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.broker.getUrl()

    @property
    def isHtml(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.broker.isHtml()

    @property
    def title(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        return self.broker.getTitle()

    @property
    def contents(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        if self._contents is None:
            self._contents = self.broker.getContent()
        return self._contents

    @property
    def headers(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        # TODO: How do we get those? Can we get them at all?
        return []

    # See zope.testbrowser.interfaces.IBrowser
    # TODO: We cannot copy this functionality here.
    handleErrors = False

    def open(self, url, data=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.broker.openUrl(url, data)
        self._stop_timer()
        self._changed()

    def _start_timer(self):
        self.timer.start()

    def _stop_timer(self):
        self.timer.stop()

    @property
    def last_request_pystones(self):
        return self.timer.elapsed_pystones

    @property
    def last_request_seconds(self):
        return self.timer.elapsed_seconds

    def reload(self):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.broker.reload()
        self._stop_timer()
        self._changed()

    def goBack(self, count=1):
        """See zope.testbrowser.interfaces.IBrowser"""
        self._start_timer()
        self.broker.goBack(count)
        self._stop_timer()
        self._changed()

    def addHeader(self, key, value):
        """See zope.testbrowser.interfaces.IBrowser"""
        # TODO: How can this be done?
        #self.mech_browser.addheaders.append( (key, value) )

    def getLink(self, text=None, url=None, id=None):
        return Link(self, text, url, id)

    def getControl(self, label=None, name=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        return Control(self, label, name, index)

    def getForm(self, id=None, name=None, action=None, index=None):
        zeroOrOne([id, name, action], '"id", "name", and "action"')
        if index is None and not any([id, name, action]):
            raise ValueError(
                'if no other arguments are given, index is required.')

        matching_forms = []
        for form in self.mech_browser.forms():
            if ((id is not None and form.attrs.get('id') == id)
            or (name is not None and form.name == name)
            or (action is not None and re.search(action, str(form.action)))
            or id == name == action == None):
                matching_forms.append(form)

        form = disambiguate(matching_forms, '', index)
        self.mech_browser.form = form
        return Form(self, form)

    def _changed(self):
        self._counter += 1
        self._contents = None


class Link(object):
    zope.interface.implements(testbrowser.interfaces.ILink)

    def __init__(self, browser, text=None, url=None, id=None):
        self.browser = browser
        self._text = text
        self._url = url
        self._id = id

        self._info = None

    def click(self):
        return self.browser.broker.executeAction(
            'clickLink', self._text, self._url, self._id)

    def getInfo(self):
        if self._info is None:
            self._info = self.browser.broker.executeAction(
                'getLinkInfo', self._text, self._url, self._id)
        return self._info

    @property
    def url(self):
        return self.getInfo()['href']

    @property
    def text(self):
        return self.getInfo()['text']

    @property
    def tag(self):
        return self.getInfo()['tag']

    @property
    def attrs(self):
        return self._info

    def __repr__(self):
        return "<%s text=%r url=%r id=%s>" % (
            self.__class__.__name__, self._text, self._url, self._id)


class Control(object):

    def __init__(self, browser, label=None, name=None, index=None):
        self.browser = browser
        self._label = label
        self._name = name
        self._index = index

    def click(self):
        return self.browser.broker.executeAction('clickControl', self._text, self._url, self._id)
