##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic traversal functionality

$Id: browser.py 5259 2004-06-23 15:59:52Z philikon $
"""

from types import FunctionType
from zope.exceptions import NotFoundError
from zope.app.traversing.adapters import DefaultTraversable
from zope.component import getView
from zope.component import getView, ComponentLookupError

class ViewTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        context = self._subject
        request = getattr(context, 'REQUEST', None)
        if request is not None:
            try:
                return getView(context, name, request).__of__(context)
            except ComponentLookupError:
                pass
        try:
            subob = super(ViewTraversable, self).traverse(name, furtherPath)
            if subob is not None:
                return subob
        except (NotFoundError, KeyError):
            pass
        raise NotFoundError(context, name)
