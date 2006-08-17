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
from cStringIO import StringIO
from test import pystone
from zope.testbrowser import interfaces
from zope.testbrowser.forms import getControl, getForm, getAllControls
from zope.testbrowser.utilities import disambiguate, any, onlyOne, zeroOrOne, \
    SetattrErrorsMixin, PystoneTimer, compressText, RegexType
import ClientForm
import mechanize
import operator
import re
import sys
import time
import urllib2

try:
    from zope import interface
except ImportError:
    from dummymodules import interface

def controlFactory(control, form, browser):
    if isinstance(control, ClientForm.Item):
        # it is a subcontrol
        return ItemControl(control, form, browser)
    else:
        t = control.type
        if t in ('checkbox', 'select', 'radio'):
            return ListControl(control, form, browser)
        elif t in ('submit', 'submitbutton'):
            return SubmitControl(control, form, browser)
        elif t=='image':
            return ImageControl(control, form, browser)
        else:
            return Control(control, form, browser)


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


class Control(SetattrErrorsMixin):
    """A control of a form."""
    interface.implements(interfaces.IControl)

    _enable_setattr_errors = False

    def __init__(self, control, form, browser):
        self.mech_control = control
        self.mech_form = form
        self.browser = browser
        self._browser_counter = self.browser._counter

        if self.mech_control.type == 'file':
            self.filename = None
            self.content_type = None

        # for some reason ClientForm thinks we shouldn't be able to modify
        # hidden fields, but while testing it is sometimes very important
        if self.mech_control.type == 'hidden':
            self.mech_control.readonly = False

        # disable addition of further attributes
        self._enable_setattr_errors = True

    @property
    def disabled(self):
        return bool(getattr(self.mech_control, 'disabled', False))

    @property
    def type(self):
        return getattr(self.mech_control, 'type', None)

    @property
    def name(self):
        return getattr(self.mech_control, 'name', None)

    @property
    def multiple(self):
        return bool(getattr(self.mech_control, 'multiple', False))

    @apply
    def value():
        """See zope.testbrowser.interfaces.IControl"""

        def fget(self):
            if (self.type == 'checkbox' and
                len(self.mech_control.items) == 1 and
                self.mech_control.items[0].name == 'on'):
                return self.mech_control.items[0].selected
            return self.mech_control.value

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            if self.mech_control.type == 'file':
                self.mech_control.add_file(value,
                                           content_type=self.content_type,
                                           filename=self.filename)
            elif self.type == 'checkbox' and len(self.mech_control.items) == 1:
                self.mech_control.items[0].selected = bool(value)
            else:
                self.mech_control.value = value
        return property(fget, fset)

    def add_file(self, file, content_type, filename):
        if not self.mech_control.type == 'file':
            raise TypeError("Can't call add_file on %s controls"
                            % self.mech_control.type)
        if isinstance(file, str):
            file = StringIO(file)
        self.mech_control.add_file(file, content_type, filename)

    def clear(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.mech_control.clear()

    def __repr__(self):
        return "<%s name=%r type=%r>" % (
            self.__class__.__name__, self.name, self.type)


class ListControl(Control):
    interface.implements(interfaces.IListControl)

    @apply
    def displayValue():
        """See zope.testbrowser.interfaces.IListControl"""
        # not implemented for anything other than select;
        # would be nice if ClientForm implemented for checkbox and radio.
        # attribute error for all others.

        def fget(self):
            return self.mech_control.get_value_by_label()

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            self.mech_control.set_value_by_label(value)

        return property(fget, fset)

    @property
    def displayOptions(self):
        """See zope.testbrowser.interfaces.IListControl"""
        res = []
        for item in self.mech_control.items:
            if not item.disabled:
                for label in item.get_labels():
                    if label.text:
                        res.append(label.text)
                        break
                else:
                    res.append(None)
        return res

    @property
    def options(self):
        """See zope.testbrowser.interfaces.IListControl"""
        if (self.type == 'checkbox' and len(self.mech_control.items) == 1 and
            self.mech_control.items[0].name == 'on'):
            return [True]
        return [i.name for i in self.mech_control.items if not i.disabled]

    @property
    def disabled(self):
        if self.type == 'checkbox' and len(self.mech_control.items) == 1:
            return bool(getattr(self.mech_control.items[0], 'disabled', False))
        return bool(getattr(self.mech_control, 'disabled', False))

    @property
    def controls(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        res = [controlFactory(i, self.mech_form, self.browser) for i in
                self.mech_control.items]
        for s in res:
            s.__dict__['control'] = self
        return res

    def getControl(self, label=None, value=None, index=None):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError

        onlyOne([label, value], '"label" and "value"')

        if label is not None:
            options = self.mech_control.get_items(label=label)
            msg = 'label %r' % label
        elif value is not None:
            options = self.mech_control.get_items(name=value)
            msg = 'value %r' % value
        res = controlFactory(
            disambiguate(options, msg, index), self.mech_form, self.browser)
        res.__dict__['control'] = self
        return res


class SubmitControl(Control):
    interface.implements(interfaces.ISubmitControl)

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._clickSubmit(self.mech_form, self.mech_control, (1,1))
        self.browser._changed()


class ImageControl(Control):
    interface.implements(interfaces.IImageSubmitControl)

    def click(self, coord=(1,1)):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.browser._clickSubmit(self.mech_form, self.mech_control, coord)
        self.browser._changed()


class ItemControl(SetattrErrorsMixin):
    interface.implements(interfaces.IItemControl)

    def __init__(self, item, form, browser):
        self.mech_item = item
        self.mech_form = form
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def control(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        res = controlFactory(
            self.mech_item._control, self.mech_form, self.browser)
        self.__dict__['control'] = res
        return res

    @property
    def disabled(self):
        return self.mech_item.disabled

    @apply
    def selected():
        """See zope.testbrowser.interfaces.IControl"""

        def fget(self):
            return self.mech_item.selected

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise interfaces.ExpiredError
            self.mech_item.selected = value

        return property(fget, fset)

    @property
    def optionValue(self):
        return self.mech_item.attrs.get('value')

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        self.mech_item.selected = not self.mech_item.selected

    def __repr__(self):
        return "<%s name=%r type=%r optionValue=%r>" % (
            self.__class__.__name__, self.mech_item._control.name,
            self.mech_item._control.type, self.optionValue)


class Form(SetattrErrorsMixin):
    """HTML Form"""
    interface.implements(interfaces.IForm)

    def __init__(self, browser, form):
        """Initialize the Form

        browser - a Browser instance
        form - a ClientForm instance
        """
        self.browser = browser
        self.mech_form = form
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def action(self):
        return self.mech_form.action

    @property
    def method(self):
        return self.mech_form.method

    @property
    def enctype(self):
        return self.mech_form.enctype

    @property
    def name(self):
        return self.mech_form.name

    @property
    def id(self):
        """See zope.testbrowser.interfaces.IForm"""
        return self.mech_form.attrs.get('id')

    def submit(self, label=None, name=None, index=None, coord=(1,1)):
        """See zope.testbrowser.interfaces.IForm"""
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        form = self.mech_form
        if label is not None or name is not None:
            intermediate, msg = getAllControls([form], label, name)
            intermediate = [
                (control, form) for (control, form) in intermediate if
                control.type in ('submit', 'submitbutton', 'image')]
            control, form = disambiguate(intermediate, msg, index)
            self.browser._clickSubmit(form, control, coord)
        else: # JavaScript sort of submit
            if index is not None or coord != (1,1):
                raise ValueError(
                    'May not use index or coord without a control')
            request = self.mech_form._switch_click("request", urllib2.Request)
            self.browser._start_timer()
            self.browser.mech_browser.open(request)
            self.browser._stop_timer()
        self.browser._changed()

    def getControl(self, label=None, name=None, index=None):
        """See zope.testbrowser.interfaces.IBrowser"""
        if self._browser_counter != self.browser._counter:
            raise interfaces.ExpiredError
        forms = [self.mech_form]
        intermediate, msg = getAllControls(forms, label, name,
                                           include_subcontrols=True)
        control, form = disambiguate(intermediate, msg, index)
        return controlFactory(control, form, self.browser)
