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
"""More convenience functions for dealing with proxies.

$Id: __init__.py,v 1.3 2003/04/16 19:32:43 bwarsaw Exp $
"""

def proxy_compatible_isinstance(obj, cls):
    """Like built-in isinstance() in Python 2.3.

    This honors __class__ if the standard isinstance() fails.  This is how it
    works in Python 2.3 so that even proxied objects will succeed the test.
    """
    if isinstance(obj, cls):
        return True
    oclass = obj.__class__
    if type(obj) == oclass:
        # Nothing more we can do
        return False
    # Note that cls may be a tuple, but issubclass can't deal with that so we
    # need to expand recursively.
    classes = {}
    flatten = [cls]
    while flatten:
        thisclass = flatten.pop(0)
        if thisclass in classes:
            continue
        if isinstance(thisclass, tuple):
            flatten.extend(list(thisclass))
        else:
            classes[thisclass] = True
    for bclass in classes.keys():
        if issubclass(oclass, bclass):
            return True
    return False
