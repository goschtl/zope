##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""PageletChooser interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

from zope.interface.common.mapping import IItemMapping, IWriteMapping

from zope.schema import Dict

from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IMacroCollector



class IMacroChooser(IMacroCollector):
    """Adapter for collect macros related to instances.
    
    The standard MacroChooser implementation will call a
    adapter providing IPageletNameManager for collecting
    the macro names.
    """

    def setDefault(name):
        """Set the default name which will be returnd if no pagelet is found.
        
        This default pagelet name has to be set every time befor we call
        the __Getitem__ method for to get a pagelet by a key. If the 
        pagelet with the given key isn't found, the __getitem__ method
        will try to find the pagelet with the default name.
        
        If you inherit your pagelet slot form the IChooseablePagelets slot 
        you can use the default name 'notfoundmacro' for to get the 
        macro called 'notfoundmacro' from the 'notfound_pagelet.pt' pagelet.
        
        """


class IChooseablePageletNames(Interface):
    """Marker interface for support IPageletNameManager adapter."""



class IPageletNameManager(Interface):
    """Marker interface for supporting pagelet name lookup.
    
    The adapter which implements this interface has to provide
    macronames which are mapped as field properties.
    """



class IAnnotatableMappingAdapter(IItemMapping, IWriteMapping):
    """Map macro keys to registred IPagelet adapter names.
    
    We use it as helper mapping for to let the macro names store to the 
    annotation.
    """

    def __getitem__(self, key):
        """Returns the macro name related to the given key."""

    def __setitem__(self, key, value):
        """Set the macro name related to the given key."""

    def __delitem__(self, key):
        """Deletes the macro name related to the given key."""



class IChooseablePagelets(IPageletSlot):
    """Base interface for chooseable pagelet slots.

    Use this interface for inherit you own chooseable slots
    where you can register your chooseable pagelets. This 
    interface shouldn't be used directly otherwise you don't
    have a possible slot interface for to support different
    slots and all registred pagelets will returned if you 
    use the vocabulary.

    If you inherit from this interface use the new interface for
    to register you own vocabulary, which returns all registred
    pagelets to the new slot interface.

    """
