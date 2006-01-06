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
"""PageletChooser Demo

$Id$
"""
__docformat__ = 'restructuredtext'


from zope.interface import implements
from zope.interface import directlyProvides

from zope.app.pageletchooser.interfaces import IAnnotatableMappingAdapter
from zope.app.pageletchooser.interfaces import IPageletNameManager

from zope.app.pageletchooser.adapters import AnnotatableMappingAdapter

from zope.app.demo.pageletchooser.interfaces import IFirstLevelPagelets

_notfound = "notfoundmacro"



class MyPageletNameAccessor(AnnotatableMappingAdapter):
    """Annotation adapter for lookup macro names by key.
    
    Setup::

        >>> from zope.interface import directlyProvides
        >>> from zope.interface import Interface
        >>> from zope.app.testing import placelesssetup, ztapi
        >>> from zope.app.annotation.interfaces import IAnnotations
        >>> from zope.app.annotation.interfaces import IAttributeAnnotatable
        >>> from zope.app.annotation.attribute import AttributeAnnotations
        >>> from zope.app.pagelet.tests import TestContext
        
        >>> placelesssetup.setUp()
        >>> ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations
        ...                     ,AttributeAnnotations)
        >>> ztapi.provideAdapter(Interface, IAnnotatableMappingAdapter
        ...                     ,MyPageletNameAccessor)

    Make test object:

        >>> obj = TestContext()
        >>> directlyProvides(obj, IAttributeAnnotatable)

    Test MyPageletNameAccessor:

        >>> mapping = IAnnotatableMappingAdapter(obj)
        >>> mapping.__setitem__('key1', 'value1')
        >>> mapping['key1']
        'value1'

        >>> mapping.__getitem__('key1')
        'value1'

        >>> mapping.__delitem__('key1')
        >>> mapping['key1']
        Traceback (most recent call last):
        ...
        KeyError: 'key1'

        >>> placelesssetup.tearDown()

    """

    implements(IFirstLevelPagelets, IAnnotatableMappingAdapter
              ,IPageletNameManager)

   
    def getFirstLevelMacroName(self):
        """Get the pagelet macro name firstlevel."""
        try:
            return self._data['firstlevel']
        except:
            return _notfound

    def setFirstLevelMacroName(self, value):
        """Set the pagelet macro name firstlevel."""
        self._data['firstlevel'] = value

    firstlevel = property(getFirstLevelMacroName, setFirstLevelMacroName)
