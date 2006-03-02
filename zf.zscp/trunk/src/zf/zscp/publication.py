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
import zope.schema

from zf.zscp import interfaces, fileformat


class Publication(object):
    """Publication"""
    zope.interface.implements(interfaces.IPublication)

    packageName = None
    name = None
    summary = None
    description = None
    homePage = None
    author = None
    authorEmail = None
    license = None
    platform = None
    classifier = None
    developersMailinglist = None
    usersMailinglist = None
    issueTracker = None
    repositoryLocation = None
    repositoryWebLocation = None
    certificationLevel = None
    certificationDate = None
    metadataVersion = None

    def __repr__(self):
        return "<%s for '%s' (meta-data version %s)>" % (
            self.__class__.__name__, self.packageName, self.metadataVersion)

def process(file):
    publication = Publication()
    processor = fileformat.HeaderProcessor(publication, interfaces.IPublication)
    processor(file)
    return publication

def produce(publication):
    producer = fileformat.HeaderProducer(publication, interfaces.IPublication)
    return producer()
