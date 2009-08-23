##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

"""
$Id$
"""

from z3c.bobopublisher.interfaces import IBrowserPage

from zope.interface import implements


class BrowserPage(object):
    """Base class for browser pages

    Verify that the class implements the interfaces:

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(IBrowserPage, BrowserPage)
        True

    Verify that the object provides the interfaces:

        >>> from zope.interface.verify import verifyObject
        >>> obj = BrowserPage(None, None)
        >>> verifyObject(IBrowserPage, obj)
        True

    """

    implements(IBrowserPage)

    def __init__(self, context, request, attribute=None):
        self.context = context
        self.request = request
        self._page_attribute = attribute

    def __call__(self):
        if hasattr(self, '_page_attribute') and \
           self._page_attribute is not None:
            return getattr(self, self._page_attribute)()
        raise NotImplementedError('__call__ method not implemented')
