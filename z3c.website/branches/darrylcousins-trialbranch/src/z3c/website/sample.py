##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import persistent
import zope.interface
import zope.component
from zope.app import folder
from zope.schema.fieldproperty import FieldProperty
from zope.app.container import btree
from zope.app.container import contained

from z3c.website import interfaces
from z3c.website import page


class Samples(btree.BTreeContainer):
    """Samples container."""

    zope.interface.implements(interfaces.ISamples)

    title = FieldProperty(interfaces.ISamples['title'])
    description = FieldProperty(interfaces.ISamples['description'])
    keyword = FieldProperty(interfaces.ISamples['keyword'])
    body = FieldProperty(interfaces.ISamples['body'])

    def __init__(self, title=None):
        super(Samples, self).__init__()
        if title is not None:
            self.title = title

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class Sample(persistent.Persistent, contained.Contained):
    """ISample implementation."""

    zope.interface.implements(interfaces.ISample)

    title = FieldProperty(interfaces.ISample['title'])
    description = FieldProperty(interfaces.ISample['description'])
    keyword = FieldProperty(interfaces.ISample['keyword'])
    body = FieldProperty(interfaces.ISample['body'])

    # infos about the sample and the author
    headline = FieldProperty(interfaces.ISample['headline'])
    summary = FieldProperty(interfaces.ISample['summary'])
    author = FieldProperty(interfaces.ISample['author'])

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)
