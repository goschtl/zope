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
$Id: dublincore.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.interface import Interface
from zope.schema import Text, TextLine, Datetime, Sequence

# XXX This will need to be filled out more.

class IDCDescriptiveProperties(Interface):
    """Basic descriptive meta-data properties
    """

    title = TextLine(
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
        value_types = (TextLine(),),
        )

    subjects = Sequence(
        title = u'Subjects',
        description = u"The unqualified Dublin Core 'Subject' element values",
        value_types = (TextLine(),),
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
        value_types = (TextLine(),),
        )




"""
$Id: dublincore.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.interface import Interface

class ICMFDublinCore(Interface):
    """This interface duplicates the CMF dublinc core interface.
    """

    def Title():
        """Return the resource title.

        The first unqualified Dublin Core 'Title' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned.
        """

    def Creator():
        """Return the resource creators.

        Return the full name(s) of the author(s) of the content
        object.

        The unqualified Dublin Core 'Creator' element values are
        returned as a sequence of unicode strings.
        """

    def Subject():
        """Return the resource subjects.

        The unqualified Dublin Core 'Subject' element values are
        returned as a sequence of unicode strings.
        """

    def Description():
        """Return the resource description

        Return a natural language description of this object.

        The first unqualified Dublin Core 'Description' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned.
        """

    def Publisher():
        """Dublin Core element - resource publisher

        Return full formal name of the entity or person responsible
        for publishing the resource.

        The first unqualified Dublin Core 'Publisher' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned.
        """

    def Contributors():
        """Return the resource contributors

        Return any additional collaborators.

        The unqualified Dublin Core 'Contributor' element values are
        returned as a sequence of unicode strings.
        """

    def Date():
        """Return the default date

        The first unqualified Dublin Core 'Date' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned. The
        string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def CreationDate():
        """Return the creation date.

        The value of the first Dublin Core 'Date' element qualified by
        'creation' is returned as a unicode string if a qualified
        element is defined, otherwise, an empty unicode string is
        returned. The string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def EffectiveDate():
        """Return the effective date

        The value of the first Dublin Core 'Date' element qualified by
        'effective' is returned as a unicode string if a qualified
        element is defined, otherwise, an empty unicode string is
        returned. The string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def ExpirationDate():
        """Date resource expires.

        The value of the first Dublin Core 'Date' element qualified by
        'expiration' is returned as a unicode string if a qualified
        element is defined, otherwise, an empty unicode string is
        returned. The string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def ModificationDate():
        """Date resource last modified.

        The value of the first Dublin Core 'Date' element qualified by
        'modification' is returned as a unicode string if a qualified
        element is defined, otherwise, an empty unicode string is
        returned. The string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def Type():
        """Return the resource type

        Return a human-readable type name for the resource.

        The first unqualified Dublin Core 'Type' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned. The
        string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def Format():
        """Return the resource format.

        Return the resource's MIME type (e.g., 'text/html',
        'image/png', etc.).

        The first unqualified Dublin Core 'Format' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned. The
        string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def Identifier():
        """Return the URL of the resource.

        This value is computed. It is included in the output of
        qualifiedIdentifiers with the qualification 'url'.
        """

    def Language():
        """Return the resource language.

        Return the RFC language code (e.g., 'en-US', 'pt-BR')
        for the resource.

        The first unqualified Dublin Core 'Language' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned. The
        string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """

    def Rights():
        """Return the resource rights.

        Return a string describing the intellectual property status,
        if any, of the resource.  for the resource.

        The first unqualified Dublin Core 'Rights' element value is
        returned as a unicode string if an unqualified element is
        defined, otherwise, an empty unicode string is returned. The
        string is formatted  'YYYY-MM-DD H24:MN:SS TZ'.
        """



__doc__ = ICMFDublinCore.__doc__ + __doc__


"""
$Id: dublincore.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.app.dublincore.general \
     import IGeneralDublinCore, IWritableGeneralDublinCore




class IZopeDublinCore(
    IGeneralDublinCore,
    IWritableGeneralDublinCore,
    ICMFDublinCore,
    IDCDescriptiveProperties,
    IDCTimes,
    IDCPublishing,
    IDCExtended,
    ):
    """Zope Dublin Core properties
    """

__doc__ = IZopeDublinCore.__doc__ + __doc__


"""
$Id: dublincore.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.app.interfaces.annotation import IAnnotatable

class IZopeDublinCoreAnnotatable(IAnnotatable):
    """Objects that can be annotated with Zope Dublin-Core meta data

    This is a marker interface that indicates the intent to have
    Zope Dublin-Core meta data associated with an object.

    """

__doc__ = IZopeDublinCoreAnnotatable.__doc__ + __doc__
