##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Select Widget Tests

$Id: test_selectwidget.py,v 1.2 2004/05/06 16:13:41 poster Exp $
"""
import unittest

from zope.schema import Choice, List
from zope.app.form.browser import SelectWidget

choice = Choice(
    title=u"Number",
    description=u"The Number",
    values=[1, 2, 3])

sequence = List(
    title=u"Numbers",
    description=u"The Numbers",
    value_type=choice)


class SelectWidgetTest(unittest.TestCase):
    
    def _makeWidget(self, form):
        request = TestRequest(form=form)
        return SelectWidget(sequence, request) 




def test_suite():
    return unittest.makeSuite(SelectWidgetTest)

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
