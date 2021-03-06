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

"""
$Id$
"""

import unittest

from zope import component
from zope import interface
from zope.testing import doctest


from zope.generic.testing.testing import InterfaceBaseTest
from zope.generic.testing.testing import registerDirective

from zope.generic.face import api
from zope.generic.face import testing


###############################################################################
#
# Unit tests  
#
###############################################################################


class FaceAdapterTest(InterfaceBaseTest):

    _verify_class = False

    @property
    def _test_interface(self):
        from zope.generic.face import IFace
        return  IFace

    @property
    def _test_class(self):
        from zope.generic.face.adapter import FaceForAttributeFaced
        return FaceForAttributeFaced

    @property
    def _test_pos(self):
        return (testing.TestAttributeFaced(),)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FaceAdapterTest),
        doctest.DocTestSuite('zope.generic.face.adapter'),
        doctest.DocTestSuite('zope.generic.face.base'),
        doctest.DocTestSuite('zope.generic.face.helper',
                             setUp=testing.placelesssetup.setUp,
                             tearDown=testing.placelesssetup.tearDown,
                             globs={'component': component, 'interface': interface,
                             'registerDirective': registerDirective,
                             'testing': testing, 'api': api},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS),
        doctest.DocFileSuite('README.txt',
                             setUp=testing.placelesssetup.setUp,
                             tearDown=testing.placelesssetup.tearDown,
                             globs={'component': component, 'interface': interface,
                             'registerDirective': registerDirective,
                             'testing': testing, 'api': api},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS),

        ))

if __name__ == '__main__': unittest.main()
