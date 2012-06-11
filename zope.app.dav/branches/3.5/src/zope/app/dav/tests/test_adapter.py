##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Test DAVSchemaAdapter

$Id$
"""
import unittest

import zope.location
from zope.location.interfaces import ILocation
from zope.location.traversing import LocationPhysicallyLocatable
from zope.testing.doctestunit import DocTestSuite
from zope.interface import Interface, implements
from zope.size.interfaces import ISized
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.annotation.interfaces import IAnnotatable, IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.filerepresentation.interfaces import IReadDirectory

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.i18nmessageid import ZopeMessageFactory as _

class IRobot(Interface):
    pass

class Robot(zope.location.Location):
    implements(IRobot, IAttributeAnnotatable)

class RobotSize(object):
    implements(ISized)

    def __init__(self, context):
        self.context = context

    def sizeForSorting(self):
        return None, None

    def sizeForDisplay(self):
        return _(u"${num} robot unit", mapping={'num': 1})

class RobotDirectory(object):
    implements(IReadDirectory)

    def __init__(self, context):
        self.context = context

def test_DAVSchemaAdapter():
    """Before we can start off, we need to provide a few basic components.
    Let's setup a minimum of the location machinery:

    >>> setUp()
    >>> ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
    ...                      LocationPhysicallyLocatable)

    Now, let's make an object and give it a name.  We can at least
    rely on it being locatable:

    >>> bender = Robot()
    >>> bender.__name__ = u'bender'

    With these minimal circumstances, the DAV adapter should still work:

    >>> from zope.app.dav.adapter import DAVSchemaAdapter
    >>> dav = DAVSchemaAdapter(bender)

    >>> dav.displayname
    u'bender'
    >>> dav.creationdate, dav.resourcetype, dav.getcontentlength
    ('', '', '')
    >>> dav.getlastmodified, dav.executable
    ('', '')

    Now, after that dull test, let's provide some actual meta-data.
    First, we have to set up the necessary adapter:

    >>> ztapi.provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations)
    >>> ztapi.provideAdapter(IAnnotatable, IWriteZopeDublinCore,
    ...                      ZDCAnnotatableAdapter)
    >>> dc = IWriteZopeDublinCore(bender)

    For example, we can set a creation date and a last modified date:

    >>> from datetime import datetime
    >>> y2k = datetime(1999, 12, 31, 23, 59, 59)
    >>> y3k = datetime(2999, 12, 31, 23, 59, 59)
    >>> dc.created = y2k
    >>> dc.modified = y3k

    Now, exercise the whole IDAVSchema again:

    >>> dav.displayname
    u'bender'
    >>> dav.creationdate == y2k.strftime('%Y-%m-%d %Z')
    True
    >>> dav.resourcetype, dav.getcontentlength
    ('', '')
    >>> dav.getlastmodified == y3k.strftime('%a, %d %b %Y %H:%M:%S GMT')
    True

    To make `getcontentlength` work, we can provide our adapter to
    `ISized`:

    >>> ztapi.provideAdapter(IRobot, ISized, RobotSize)
    >>> dav.getcontentlength
    ''

    And if robots were directories:

    >>> ztapi.provideAdapter(IRobot, IReadDirectory, RobotDirectory)

    then the adapter would actually tell us:

    >>> dav.displayname
    u'bender/'

    >>> import xml.dom.minidom
    >>> isinstance(dav.resourcetype, xml.dom.minidom.Element)
    True
    >>> dav.resourcetype.localName
    'collection'

    All there is now to it is cleaning up after ourselves:

    >>> tearDown()
    """

def test_suite():
    return unittest.TestSuite((
            DocTestSuite(),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
