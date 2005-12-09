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
"""XXX short summary goes here.

$Id$
"""
import unittest
from zope.testing import doctest

def type_errors():
    """
You can pass unicode strings, or strings:

    >>> from zope.ucol import Collator
    >>> c = Collator('root')
    >>> c.key(u"Hello") == c.key("Hello")
    True
    >>> c.cmp(u"Hello", "Hello")
    0

As long as the strings can be decoded as ASCII:

    >>> c.key("Hello\xfa")
    Traceback (most recent call last):
    ...
    UnicodeDecodeError: 'ascii' codec can't decode byte
    0xfa in position 5: ordinal not in range(128)

    >>> c.cmp(u"Hello", "Hello\xfa")
    Traceback (most recent call last):
    ...
    UnicodeDecodeError: 'ascii' codec can't decode byte
    0xfa in position 5: ordinal not in range(128)

And you can't pass a non-string:

    >>> c.key(0)
    Traceback (most recent call last):
    ...
    TypeError: Expected unicode string

    >>> c.cmp(u"Hello", 0)
    Traceback (most recent call last):
    ...
    TypeError: Expected unicode string

"""

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocTestSuite('zope.ucol',
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

