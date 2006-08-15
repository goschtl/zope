##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
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
"""Functional tests for the comment text widgets.

"""
__docformat__ = "reStructuredText"

import unittest

from zope import interface, component
import zope.publisher.browser

import zope.app.form.interfaces
import zope.app.testing.functional

import zc.comment.interfaces
import zc.comment.browser.widget


class IFace(interface.Interface):

    foo = zc.comment.interfaces.CommentText(
        title=u"Foo",
        description=u"Foo description",
        )

class Face(object):

    foo = (u"Foo<br />\n"
           u"\n"
           u"Bar &lt; &amp; &gt;")


class WidgetConfigurationTestCase(
    zope.app.testing.functional.FunctionalTestCase):

    """Check that configure.zcml sets up the widgets as expected."""

    def setUp(self):
        super(WidgetConfigurationTestCase, self).setUp()
        self.field = IFace["foo"]
        self.bound_field = self.field.bind(Face())
        self.request = zope.publisher.browser.TestRequest()

    def test_display_widget_lookup(self):
        w = component.getMultiAdapter(
            (self.bound_field, self.request),
             zope.app.form.interfaces.IDisplayWidget)
        self.failUnless(isinstance(w,
                                   zc.comment.browser.widget.Display))

    def test_input_widget_lookup(self):
        w = component.getMultiAdapter(
            (self.bound_field, self.request),
             zope.app.form.interfaces.IInputWidget)
        self.failUnless(isinstance(w, zc.comment.browser.widget.Input))


def test_suite():
    return unittest.makeSuite(WidgetConfigurationTestCase)
