##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from zope.testing import setupstack
import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import unittest

def test_testing_error_on_unicode_and_other_types():
    """
    >>> import zc.metarecipe.testing
    >>> buildout = zc.metarecipe.testing.Buildout()

    Strings are cool:

    >>> buildout._raw['x'] = dict(o='v')
    >>> _ = buildout['x']
    [x]
    o = v

    Unicode not so much:

    >>> buildout._raw['x'] = dict(o=u'v')
    >>> _ = buildout['x']
    Traceback (most recent call last):
    ...
    TypeError: ('Option values must be strings', u'v')

    Or other non strings:

    >>> buildout._raw['x'] = dict(o=1)
    >>> _ = buildout['x']
    Traceback (most recent call last):
    ...
    TypeError: ('Option values must be strings', 1)

    """

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.txt',
            setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown,
            ),
        doctest.DocTestSuite(),
        ))

