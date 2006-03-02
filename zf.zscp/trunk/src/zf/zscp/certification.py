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
"""Certification

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

from zf.zscp import interfaces, fileformat, contact


class Certification(object):
    """Certification Implementation."""
    zope.interface.implements(interfaces.ICertification)

    action = None
    sourceLevel = None
    targetLevel = None
    date = None
    certificationManger = None
    comments = None

    def __repr__(self):
        return '<%s action=%r, source=%r, target=%r>' % (
            self.__class__.__name__, self.action,
            self.sourceLevel, self.targetLevel)


_rootField = zope.schema.List(
    value_type=zope.schema.Object(schema=interfaces.ICertification))

def processXML(xml):
    """Process the XML to create a list of certifications."""
    handler = fileformat.XMLHandler(
        'certifications', _rootField,
        {interfaces.IContact: contact.Contact,
         interfaces.ICertification: Certification})
    return fileformat.processXML(xml, handler)

def produceXML(certifications):
    """Convert the list of certifications to XML."""
    producer = fileformat.InfoProducer(certifications, _rootField)
    return fileformat.produceXML(producer, 'certification.xmlt')
