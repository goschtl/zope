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
"""Test directly implemented functions in zapi

$Id: test_zapi.py,v 1.2 2003/05/27 14:18:26 jim Exp $
"""

from zope.testing.doctestunit import DocTestSuite
from zope.context import ContextWrapper
from zope.app import zapi

def test_name():
    """
    >>> ob = []
    >>> zapi.name(ob)
    >>> ob = zapi.ContextWrapper(ob, None, name='bob')
    >>> zapi.name(ob)
    'bob'
    """

def test_suite(): return DocTestSuite()
if __name__ == '__main__': unittest.main()
