##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Release

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

from zf.zscp import interfaces, fileformat, contact

class Release(object):
    """Release Implementation."""
    zope.interface.implements(interfaces.IRelease)

    name = None
    version = None
    codename = None
    date = None
    certification = None
    package = None
    source = None
    dependencies = None
    announcement = None
    releaseManager = None
    pressContact = None

    def __repr__(self):
        return '<%s name=%r, version=%r, codename=%r>' % (
            self.__class__.__name__, self.name, self.version, self.codename)


_rootField = zope.schema.List(
    value_type=zope.schema.Object(schema=interfaces.IRelease))

def processXML(xml):
    """Process the XML to create a list of releases."""
    handler = fileformat.XMLHandler(
        'releases', _rootField,
        {interfaces.IContact: contact.Contact, interfaces.IRelease: Release})
    return fileformat.processXML(xml, handler)

def produceXML(releases):
    """Convert the list of releases to XML."""
    producer = fileformat.InfoProducer(releases, _rootField)
    return fileformat.produceXML(producer, 'release.xmlt')
