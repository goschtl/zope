##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""MIME type guessing framework interface definitions

$Id$
"""
from zope.interface import Interface
from zope.schema import ASCIILine, TextLine


class IMIMETypesUtility(Interface):
    """MIME type guessing utility"""
    
    def getTypeByFileName(filename):
        """Return type guessed by filename"""
    
    def getTypeByContents(file, min_priority=0, max_priority=100):
        """Return type guessed by data. Accepts file-like object"""
        
    def getType(filename=None, file=None):
        """Guess content type either by file name or contents or both.
        
        At least one of these arguments should be provided.
        
        This method always returns some useful mimetype, 
        ``application/octet-stream`` or ``text/plain``.
        """


class IMIMEType(Interface):
    """Single MIME type representation"""
    
    media = ASCIILine(
        title=u'Media',
        required=True,
        readonly=True)

    subtype = ASCIILine(
        title=u'Subtype',
        required=True,
        readonly=True)

    title = TextLine(
        title=u'Title',
        required=True,
        readonly=True)

    def __str__():
        """Return a ``media/subtype`` presentation of mime type"""


class IConvenienceAPI(Interface):
    """Convenience API to be provided by the __init__ module."""
    
    def getType(filename=None, file=None):
        """Guess content type either by file name or contents or both
        
        See IMIMETypesUtility.getType documentation.
        """
    
    def lookup(media, subtype=None):
        """Return a IMIMEType object for given string representation.
        
        If ``media`` argument is in the "media/subtype" form, then the
        ``subtype`` argument should't be specified and will be extracted
        from the ``media`` argument.
        """
