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

$Id: attributeannotations.py,v 1.5 2003/06/01 15:59:25 jim Exp $
"""

from zodb.btrees.OOBTree import OOBTree
from zope.app.interfaces.annotation import IAnnotations
from zope.proxy import removeAllProxies
from zope.app.context import ContextWrapper

class AttributeAnnotations:
    """
    Store annotations in the __annotations__ attribute on a
    IAttributeAnnotatable object.
    """

    __implements__ = IAnnotations

    def __init__(self, obj):
        # We could remove all proxies from obj at this point, but
        # for now, we'll leave it to users of annotations to do that.
        # Users of annotations will typically need to do their own
        # unwrapping anyway.

        self.wrapped_obj = obj
        self.unwrapped_obj = removeAllProxies(obj)

    def __getitem__(self, key):
        annotations = getattr(self.unwrapped_obj, '__annotations__', {})
        return ContextWrapper(annotations[key], self.wrapped_obj)

    def get(self, key, default=None):
        try:
            value = self.unwrapped_obj.__annotations__.get(key, default)
        except AttributeError:
            # I guess default shouldn't be wrapped.
            return default
        else:
            return ContextWrapper(value, self.wrapped_obj)

    def __getattr__(self, name):
        # this method is for getting methods and attributes of the
        # mapping object used to store annotations.
        try:
            attr = getattr(self.unwrapped_obj.__annotations__, name)
        except AttributeError:
            if not hasattr(self.unwrapped_obj, '__annotations__'):
                annotations = self.unwrapped_obj.__annotations__ = OOBTree()
                attr = getattr(annotations, name)
            else:
                raise
        return ContextWrapper(attr, self.wrapped_obj)
