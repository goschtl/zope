##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit test helper that uses doctest

$Id: doc.py,v 1.1 2003/04/18 21:42:45 jim Exp $
"""

import sys
from StringIO import StringIO
from doctest import testmod

def doctest(testcase, module):

    old = sys.stdout
    new = StringIO()
    try:
        sys.stdout = new
        failures, tries = testmod(module, isprivate=lambda *a: False)
    finally:
        sys.stdout = old

    testcase.failIf(failures, new.getvalue())
