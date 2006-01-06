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
"""PageletChooser adapters

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent.dict import PersistentDict

from zope.security.proxy import removeSecurityProxy

from zope.interface import implements

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.pageletchooser.interfaces import IAnnotatableMappingAdapter

annotation_key = "zope.app.pageletchooser.pageletnamemapping"



class AnnotatableMappingAdapter(object):
    """Abstract adapter base class for to store a pagelet name mapping.
    
    This adapter uses the annotation key 
    'zope.app.pageletchooser.pageletnamemapping' for to store the mapping
    which is just a persistent dict.
    
    Inherit from this base adapter class for to store the pagelet names
    in the annotation. Your implementation has also to support your own
    pagelet name schema. The pagelet names are stored in persistent dict
    in the annotation of the object. To access this dict data use a 
    adapter which maps the dict data to field property.  This let's you
    register a edit view for to edit the pagelet names. You can use the
    vocabular PageletNamesVocabulary for to lookup the registred pagelet 
    names in the fields.
    
    For a example look at the package: zope.app.demo.pageletchooser.

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
        ...                     ,AnnotatableMappingAdapter)

    Make test object:

        >>> obj = TestContext()
        >>> directlyProvides(obj, IAttributeAnnotatable)

    Test AnnotatableMappingAdapter:

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

    """

    implements(IAnnotatableMappingAdapter)


    def __init__(self, context=None):
        context = removeSecurityProxy(context)
        self.context = context
        self._annotations = IAnnotations(context)
        
        if not self._annotations.get(annotation_key):
            self._annotations[annotation_key] = PersistentDict()
        
        self._data = self._annotations.get(annotation_key)
        
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        
    def __delitem__(self, key):
        del self._data[key]
