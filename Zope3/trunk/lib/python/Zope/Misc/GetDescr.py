##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
Get a descriptor corresponding to an attribute.

Revision information:
$Id: GetDescr.py,v 1.3 2002/09/28 01:02:39 gvanrossum Exp $
"""

def GetDescr(obj, name):
    """
    Get the descriptor for obj.<name>, if one exists.

    Arguments:
    obj:  the object; must be a new-style instance
    name: the attribute name; must be a string

    Return a descriptor (something implementing __get__) that controls
    (at least read) access to obj.<name>, or None if obj.<name> is not
    controlled by a descriptor, or if obj.<name> does not exist.

    Examples:

    1. If the attribute is a property, it is definitely returned.
    2. If the attribute is a method, it is returned unless it is
       overridden in obj.__dict__.
    3. If the attribute is a simple value (e.g. an int), either stored
       in obj.__dict__ or as a class attribute, None is returned.
    4. If the attribute doesn't exist, None is returned.
    """
    if not isinstance(obj.__class__, type):
        raise TypeError("obj must be a new-style instance")
    if not isinstance(name, (str, unicode)):
        raise TypeError("name must be a string")
    try:
        d = obj.__dict__
    except AttributeError:
        isivar = 0
    else:
        isivar = name in d
    for cls in obj.__class__.__mro__:
        d = cls.__dict__
        if name in d:
            found = d[name]
            break
    else:
        return None
_loop_callbacks    if not hasattr(found, "__get__"):
        return None
    if not isivar or hasattr(found, "__set__"):
        return found
    return None
