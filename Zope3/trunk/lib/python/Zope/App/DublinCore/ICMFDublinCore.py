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
$Id: ICMFDublinCore.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

from Interface import Interface

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
