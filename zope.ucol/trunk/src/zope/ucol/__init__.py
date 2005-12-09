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
your locale.  We'll use the special "root" locale in this example:

    >>> import zope.ucol
    >>> collator = zope.ucol.Collator("root")

The collator has a key method for creating collation keys from unicode
strings.  The method can be passed as the key argument to list.sort
or to the built-in sorted function.

    >>> sorted([u'Sam', u'sally', u'Abe', u'alice', u'Terry', u'tim',
    ...        u'\U00023119', u'\u62d5'], key=collator.key)
    [u'Abe', u'alice', u'sally', u'Sam', u'Terry', u'tim', 
     u'\u62d5', u'\U00023119']

There is a cmp method for comparing 2 unicode strings, which can also be
used when sorting:

    >>> sorted([u'Sam', u'sally', u'Abe', u'alice', u'Terry', u'tim',
    ...        u'\U00023119', u'\u62d5'], collator.cmp)
    [u'Abe', u'alice', u'sally', u'Sam', u'Terry', u'tim', 
     u'\u62d5', u'\U00023119']

Note that it is almost always more efficient to pass the key method to
sorting functions, rather than the cmp method.  The cmp method is more
efficient in the special case that strings are long and few and when
they tend to differ at their beginnings.  This is because computing
the entire key can be much more expensive than comparison when the
order can be determined based on analyzing a small portion of the
original strings.

You can ask a collator for it's locale:

    >>> collator.locale
    'root'

and you can find out whether default collation information was used:

    >>> collator.used_default_information
    0
    >>> collator = zope.ucol.Collator("eek")
    >>> collator.used_default_information
    1

$Id$
"""

from _zope_ucol import Collator
