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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: ntests.py 4280 2005-12-01 21:39:17Z benji $
"""

import persistent
import pytz
import re
import unittest
from zope.testing import doctest
from zope import component, interface
import zope.interface.common.idatetime
import zope.testing.renormalizing
import zc.table

from zope.app.testing.functional import defineLayer


class MyContent(persistent.Persistent):
    x = 0

@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def requestToTZInfo(request):
    return pytz.timezone('US/Eastern')

def formatterFactory(*args, **kw):
    return zc.table.table.FormFullFormatter(*args, **kw)
interface.directlyProvides(formatterFactory,
                           zc.table.interfaces.IFormatterFactory)

defineLayer('CommentLayer')

def test_suite():
    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile(r'\d\d\d\d \d\d? \d\d?\s+\d\d:\d\d:\d\d( [+-]\d+)?'),
         'YYYY MM DD  HH:MM:SS'),
        ])
    suite = doctest.DocFileSuite('browser/comments.txt', checker=checker,
                                 optionflags=doctest.NORMALIZE_WHITESPACE |
                                             doctest.ELLIPSIS)
    suite.layer = CommentLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

