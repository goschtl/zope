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
"""Publication

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface

from zope.schema.fieldproperty import FieldProperty
from zf.zscp.interfaces import IPublication
from zf.zscp.fileformat import HeaderProcessor
from zf.zscp.fileformat import HeaderProducer


class Publication(object):
    """Publication"""
    zope.interface.implements(IPublication)

    def __init__(self):
        self.packageName = None
        self.name = None
        self.summary = None
        self.description = None
        self.homePage = None
        self.author = []
        self.authorEmail = []
        self.license = []
        self.platform = []
        self.classifier = []
        self.developersMailinglist = None
        self.usersMailinglist = None
        self.issueTracker = None
        self.repositoryLocation = None
        self.repositoryWebLocation = None
        self.certificationLevel = None
        self.certificationDate = None
        self.metadataVersion = None

    def __repr__(self):
        return "<%s for '%s' (meta-data version %s)>" % (
            self.__class__.__name__, self.packageName, self.metadataVersion)

def process(file):
    publication = Publication()
    processor = HeaderProcessor(publication, IPublication)
    processor(file)
    return publication

def produce(publication):
    producer = HeaderProducer(publication, IPublication)
    return producer()
