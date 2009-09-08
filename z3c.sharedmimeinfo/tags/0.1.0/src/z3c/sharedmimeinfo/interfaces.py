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
from zope.schema import TextLine


class IMIMETypesUtility(Interface):
    """MIME type guessing utility"""
    
    def getTypeByFileName(filename):
        """Guess type by filename.
        
        Return an IMIMEType object or None, if no matching mime type found.
        """
    
    def getTypeByContents(file, min_priority=0, max_priority=100):
        """Guess type by data, using "magic" (byte matching).
        
        file argument is a file-like object.

        min_priority and max_priority control the range of magic rules to use,
        rules with lower priority are more generic, while ones with higher
        priority are more specific. See shared-mime-info specification for
        more details.
        
        Return an IMIMEType object or None, if not matching mime type found.
        """
        
    def getType(filename=None, file=None):
        """Guess content type either by file name or contents or both.
        
        filename is a string, file is a file-like object. At least one of
        these arguments should be provided.
        
        This method always returns an usable IMIMEType object, using
        application/octet-stream and text/plain as fallback mime types.
        """


class IMIMEType(Interface):
    """MIME type representation
    
    Objects providing this interface also act as the unicode strings with
    the <media>/<subtype> value.
    """
    
    media = TextLine(title=u'Media', required=True, readonly=True)
    subtype = TextLine(title=u'Subtype', required=True, readonly=True)
    title = TextLine(title=u'Title', required=True, readonly=True)
