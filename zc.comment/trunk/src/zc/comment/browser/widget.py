##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Widgets for rich text fields.

The *rich text* supported by these widgets is very simple, but we
expect this to be forward-compatible with more elaborate rich text
support in the future.

The input is a conventional XHTML textarea; newlines are converted to
<br/> elements and other characters are encoded into XHTML entity
references as needed.

"""
__docformat__ = "reStructuredText"

import HTMLParser
import xml.sax.saxutils

import zope.app.form.browser.textwidgets
import zope.app.form.browser.widget


class Input(zope.app.form.browser.textwidgets.TextAreaWidget):

    cssClass = "zc-comment-text"

    def _toFieldValue(self, value):
        if value:
            # normalize newlines:
            value = value.replace("\r\n", "\n")
            value = value.replace("\r", "\n")
            # encode magical characters:
            value = xml.sax.saxutils.escape(value)
            # add <br/> tags:
            value = value.replace("\n", "<br />\n")
        return value

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return ""
        if value:
            # rip out XHTML encoding, converting markup back to plain text
            # (we're encoding simple rich text as plain text!)
            p = ConversionParser()
            p.feed(value)
            p.close()
            value = p.get_data()
        return value

    def __call__(self):
        return zope.app.form.browser.widget.renderElement(
            "textarea",
            name=self.name,
            id=self.name,
            cssClass=self.cssClass,
            rows=self.height,
            cols=self.width,
            style=self.style,
            contents=self._getFormValue(), # already escaped
            extra=self.extra,
            )

class Display(zope.app.form.browser.widget.DisplayWidget):

    cssClass = "zc-comment-text"
    tag = "div"

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        if self.tag:
            value = zope.app.form.browser.widget.renderElement(
                self.tag, cssClass=self.cssClass, contents=value)
        return value


class ConversionParser(HTMLParser.HTMLParser):

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.__buffer = []

    def handle_data(self, data):
        self.__buffer.append(data)

    def handle_entityref(self, name):
        self.__buffer.append("&%s;" % name)

    def get_data(self):
        return "".join(self.__buffer)
