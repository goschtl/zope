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

$Id: __init__.py,v 1.5 2003/04/19 10:34:38 srichter Exp $
"""
from types import ClassType
from zope.proxy.introspection import removeAllProxies


def proxy_compatible_isinstance(obj, cls):
    """Like built-in isinstance() in Python 2.3.

    This honors __class__ if the standard isinstance() fails.  This is how it
    works in Python 2.3 so that even proxied objects will succeed the test.
    """
    if isinstance(obj, cls):
        return True
    # Check whether the object is a class itself, if so abort, otherwise the
    # next check will fail.
    if type(removeAllProxies(obj)) == ClassType:
        return False
    oclass = removeAllProxies(obj.__class__)
    if type(obj) is oclass:
        # Nothing more will help
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
            flatten.extend(thisclass)
        else:
            classes[thisclass] = True
    for bclass in classes.keys():
        if issubclass(oclass, bclass):
            return True
    return False
