##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: PropertySchemas.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

from Interface import Interface
from Zope.Schema import Text, Datetime, Sequence

# XXX This will need to be filled out more.

class IDCDescriptiveProperties(Interface):
    """Basic descriptive meta-data properties
    """

    title = Text(
        title = u'Title',
        description =
        u"The first unqualified Dublin Core 'Title' element value."
        )

    description = Text(
        title = u'Description',
        description =
        u"The first unqualified Dublin Core 'Description' element value.",
        )

class IDCTimes(Interface):
    """Time properties
    """

    created = Datetime(
        title = u'Creation Date',
        description =
        u"The date and time that an object is created. "
        u"\nThis is normally set automatically."
        )
    
    modified = Datetime(
        title = u'Modification Date',
        description =
        u"The date and time that the object was last modified in a\n"
        u"meaningful way."
        )

class IDCPublishing(Interface):
    """Publishing properties
    """

    effective = Datetime(
        title = u'Effective Date',
        description =
        u"The date and time that an object should be published. "
        )
    

    expires = Datetime(
        title = u'Expiration Date',
        description =
        u"The date and time that the object should become unpublished."
        )

class IDCExtended(Interface):
    """Extended properties

    This is a mized bag of properties we want but that we probably haven't
    quite figured out yet.
    """


    creators = Sequence(
        title = u'Creators',
        description = u"The unqualified Dublin Core 'Creator' element values",
        value_types = (Text(),),
        )

    subjects = Sequence(
        title = u'Subjects',
        description = u"The unqualified Dublin Core 'Subject' element values",
        value_types = (Text(),),
        )

    publisher = Text(
        title = u'Publisher',
        description =
        u"The first unqualified Dublin Core 'Publisher' element value.",
        )

    contributors = Sequence(
        title = u'Contributors',
        description =
        u"The unqualified Dublin Core 'Contributor' element values",
        value_types = (Text(),),
        )
    

