##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Test the Choice display and edit widget (function).

$Id$
"""
import unittest
from zope.component.testing import PlacelessSetup
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IChoice, IIterableVocabulary
from zope.schema import Choice

from zope.app.testing import ztapi
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.app.form.browser import ChoiceDisplayWidget, ChoiceInputWidget
from zope.app.form.browser import ItemDisplayWidget, DropdownWidget


class ChoiceWidgetTest(PlacelessSetup, unittest.TestCase):

    def test_ChoiceDisplayWidget(self):
        ztapi.provideMultiView((IChoice, IIterableVocabulary), IBrowserRequest,
                               IDisplayWidget, '', ItemDisplayWidget)
        field = Choice(values=[1, 2, 3])
        bound = field.bind(object())
        widget = ChoiceDisplayWidget(bound, TestRequest())
        self.assert_(isinstance(widget, ItemDisplayWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.vocabulary)


    def test_ChoiceInputWidget(self):
        ztapi.provideMultiView((IChoice, IIterableVocabulary), IBrowserRequest,
                               IInputWidget, '', DropdownWidget)
        field = Choice(values=[1, 2, 3])
        bound = field.bind(object())
        widget = ChoiceInputWidget(bound, TestRequest())
        self.assert_(isinstance(widget, DropdownWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.vocabulary)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ChoiceWidgetTest),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
