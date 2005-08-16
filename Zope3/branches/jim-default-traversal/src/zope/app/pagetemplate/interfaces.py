##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces for apis to make available to TALES

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.dublincore.interfaces import IDCDescriptiveProperties
from zope.app.dublincore.interfaces import IDCTimes
from zope.interface import Interface

class IZopeTalesAPI(IDCDescriptiveProperties, IDCTimes):

    def name():
        """Return the object's name

        This is the name the object is stored under in the container
        it was accessed in.
        """

    def title_or_name():
        """Return the title, if the is one, or the name otherwise
        """

    def size():
        """Return a string representing the size of the object

        This string could be a collection of digits or a descriptive
        string of some sort.  If the size can't be determined
        (e.g. the object has no size), an empty string is returned.
        """
    
class IURLQuote(Interface):

    def quote():
        """Return the objects URL quote representation."""

    def quote_plus():
        """Return the objects URL quote_plus representation."""

    def unquote():
        """Return the objects URL unquote representation."""

    def unquote_plus():
        """Return the objects URL unquote_plus  representation."""

