##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""Package zope.generic.directlyprovides.

$Id$
"""

import unittest

from zope import component
from zope import interface
from zope import schema
from zope.testing import doctest

from zope.generic.directlyprovides.testing import placelesssetup 
from zope.generic.testing.testing import registerDirective


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.generic.directlyprovides.helper'),
        doctest.DocTestSuite('zope.generic.directlyprovides.property'),
        doctest.DocTestSuite('zope.generic.directlyprovides.event'),
        doctest.DocFileSuite('README.txt',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown,
                             globs={'component': component, 'interface': interface,
                                'schema': schema, 'registerDirective': registerDirective},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS),
        ))

if __name__ == '__main__': unittest.main()
