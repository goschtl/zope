##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the ChoiceSequence display and edit widget (function).

$Id: test_choicesequencetest.py,v 1.1 2004/04/24 23:19:07 srichter Exp $
"""
import unittest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IChoiceSequence, IIterableVocabulary
from zope.schema import Choice, Sequence

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.app.form.browser import ChoiceSequenceDisplayWidget
from zope.app.form.browser import ChoiceSequenceEditWidget
from zope.app.form.browser import ItemsMultiDisplayWidget, SelectWidget


def provideMultiView(for_, factory, providing, name='', layer="default"):
    s = zapi.getService(None, zapi.servicenames.Presentation)
    return s.provideAdapter(IBrowserRequest, factory, name, for_,
                            providing, layer)


class ChoiceSequenceWidgetTest(PlacelessSetup, unittest.TestCase):

    def test_ChoiceSequenceDisplayWidget(self):
        provideMultiView((IChoiceSequence, IIterableVocabulary),
                         ItemsMultiDisplayWidget, IDisplayWidget)
        field = Sequence(value_type=Choice(values=[1, 2, 3]))
        bound = field.bind(object())
        widget = ChoiceSequenceDisplayWidget(bound, TestRequest())
        self.assert_(isinstance(widget, ItemsMultiDisplayWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.value_type.vocabulary)


    def test_ChoiceSequenceEditWidget(self):
        provideMultiView((IChoiceSequence, IIterableVocabulary),
                         SelectWidget, IInputWidget)
        field = Sequence(value_type=Choice(values=[1, 2, 3]))
        bound = field.bind(object())
        widget = ChoiceSequenceEditWidget(bound, TestRequest())
        self.assert_(isinstance(widget, SelectWidget))
        self.assertEqual(widget.context, bound)
        self.assertEqual(widget.vocabulary, bound.value_type.vocabulary)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ChoiceSequenceWidgetTest),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
