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
"""Renderable Text Object.

$Id$
"""
from zope.security.checker import defineChecker, NoProxy

class RenderableText(unicode):
    """An extension to unicode to keep track of text's type.

    In general you can store anything in the 'ttype' slot. However, to make this
    attribute useful in the context of the bugtracker, the 'ttype' must
    *always* contain a valid source type as specified in the zope.app.renderer
    package.

    Here a simple example on using the slot:

      >>> rt = RenderableText('foo bar')
      >>> rt
      u'foo bar'
      >>> rt.ttype
      u'zope.source.rest'
      >>> rt.ttype = u'zope.source.plaintext'
      >>> rt.ttype
      u'zope.source.plaintext'

      >>> rt = RenderableText(u'foo bar', u'zope.source.stx')
      >>> rt
      u'foo bar'
      >>> rt.ttype
      u'zope.source.stx'
    """

    __slots__ = ('ttype',)

    def __new__(cls, ustr, ttype=None):
        """Create a new RenderableText object."""
        self = unicode.__new__(cls, ustr)
        self.ttype = ttype or u'zope.source.rest'
        return self

    def __getstate__(self):
        """Return the state of the object."""
        return unicode(self), self.ttype

    def __setstate__(self, (ustr, ttype)):
        """Set the state of the object."""
        super(RenderableText, self).__init__(ustr)
        self.ttype = ttype


# Make sure the renderable texts get never proxied
defineChecker(RenderableText, NoProxy)
