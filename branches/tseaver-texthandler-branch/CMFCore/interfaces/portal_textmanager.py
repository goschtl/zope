##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

"""
    Text manager tool interface description.
"""


from Interface import Attribute, Base
from Interface.Mapping import MinimalDictionary

RAISE_KEY_ERROR = []

class TextInfo( MinimalDictionary ):
    """
        Represent a (potentially processed) chunk of textual content,
        along with arbitrary extra data.
    """
    def getText():
        """
            Return the (possibly modified) text.
        """
    
    __call__ = getText

class TextFilter( Base ):
    """
        Process raw textual content into sanitized HTML.
    """
    def filterText( text_info='' ):
        """
            Process 'text_info', which may be either a string
            or a TextInfo implementation;  return a TextInfo.
        """

    __call__ = filterText

class portal_textmanager(Base):
    """
        Interface for tool which registers and hands out TextFilter
        implementations.
    """

    def registerTextFilter( type_name, format, filter ):
        """
            Register 'filter' (which must implement TextFilter)
            to be used for objects whose Type is 'type_name' and
            whose Formate is 'format'.
        """

    def getTextFilter( type_name, format ):
        """
            Retrieve the registered filter for 'type_name' and 'format'.
        """
