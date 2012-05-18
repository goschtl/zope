##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Tests for the unique id utility.

$Id$
"""
import unittest
from zope.testing import doctest

def test_imports():
    """
    All functionality was moved to zope.keyreference, so the tests are
    moved as well. Here, we only test that backward-compatibility imports
    are still working.

    >>> from zope.app.keyreference.interfaces import NotYet, IKeyReference
    >>> NotYet.__module__
    'zope.keyreference.interfaces'
    >>> IKeyReference
    <InterfaceClass zope.keyreference.interfaces.IKeyReference>

    >>> from zope.app.keyreference.persistent import KeyReferenceToPersistent
    >>> from zope.app.keyreference.persistent import connectionOfPersistent
    >>> KeyReferenceToPersistent
    <class 'zope.keyreference.persistent.KeyReferenceToPersistent'>
    >>> connectionOfPersistent
    <function connectionOfPersistent at 0x...>

    >>> from zope.app.keyreference.testing import SimpleKeyReference
    >>> SimpleKeyReference
    <class 'zope.keyreference.testing.SimpleKeyReference'>
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(optionflags=doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
