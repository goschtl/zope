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
"""Locale-based text collation using ICU

The zope.ucol package provides a minimal Pythonic wrapper around the
u_col C API of the International Components for Unicode (ICU) library.
It provides locale-based text collation.

To perform collation, you need to create a collator key factory for
your locale.  We'll use the "root" locale:

    >>> import zope.ucol
    >>> key = zope.ucol.KeyFactory("root")

The factory is a callable for creating collation keys from unicode
strings.  The factory can be passed as the key argument to list.sort
or to the built-in sorted function.

    >>> sorted([u'Sam', u'sally', u'Abe', u'alice', u'Terry', u'tim',
    ...        u'\U00023119', u'\u62d5'], key=key)
    [u'Abe', u'alice', u'sally', u'Sam', u'Terry', u'tim', 
     u'\u62d5', u'\U00023119']


$Id$
"""

from _zope_ucol import KeyFactory
