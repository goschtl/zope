##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

import persistent
from zope import interface

from zope.schema.fieldproperty import FieldProperty

from zope.app.container.contained import Contained
from zope.app.container import btree
from zope.app.folder.folder import Folder

from lovely.tag.interfaces import ITaggable
from lovely.tag.performance.interfaces import IUrl, IUrlContainer, IPerformanceTestSite


class PerformanceTestSite(Folder):
    interface.implements(IPerformanceTestSite)

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.__name__)


class Url(persistent.Persistent, Contained):
    interface.implements(IUrl, ITaggable)

    url = FieldProperty(IUrl['url'])


class UrlContainer(btree.BTreeContainer):
    interface.implements(IUrlContainer)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

