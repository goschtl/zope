##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id$
"""
from zope.interface import implements
from zope.app.index.interfaces import IInterfaceIndexer

class InterfaceIndexingSubscriber(object):
    """Index interface-defined fields

       Mixin for indexing a particular field name, after first adapting the
       object to be indexed to an interface.

       The class is meant to be mixed with a base class that defines an
       index_doc method:
       
         >>> class BaseIndex(object):
         ...     def __init__(self):
         ...         self.data = []
         ...     def index_doc(self, id, value):
         ...         self.data.append((id, value))

       The class does two things. The first is to get a named field
       from an object:

         >>> class Data:
         ...     def __init__(self, v):
         ...         self.x = v

         >>> class Index(InterfaceIndexingSubscriber, BaseIndex):
         ...     pass

         >>> index = Index('x')
         >>> index.index_doc(11, Data(1))
         >>> index.index_doc(22, Data(2))
         >>> index.data
         [(11, 1), (22, 2)]

       A method can be indexed:

         >>> Data.z = lambda self: self.x + 20
         >>> index = Index('z')
         >>> index.index_doc(11, Data(1))
         >>> index.index_doc(22, Data(2))
         >>> index.data
         [(11, 21), (22, 22)]
         
       The class can also adapt an object to an interface:

         >>> from zope.interface import Interface
         >>> class I(Interface):
         ...     pass

         >>> class Data:
         ...     def __init__(self, v):
         ...         self.x = v
         ...     def __conform__(self, iface):
         ...         if iface is I:
         ...             return Data2(self.x)

         >>> class Data2:
         ...     def __init__(self, v):
         ...         self.y = v*v
         
         >>> index = Index('y', I)
         >>> index.index_doc(11, Data(3))
         >>> index.index_doc(22, Data(2))
         >>> index.data
         [(11, 9), (22, 4)]

       When you define an index class, you can define a default
       interface and/or a default interface:

         >>> class Index(InterfaceIndexingSubscriber, BaseIndex):
         ...     default_interface = I
         ...     default_field_name = 'y'
        
         >>> index = Index()
         >>> index.index_doc(11, Data(3))
         >>> index.index_doc(22, Data(2))
         >>> index.data
         [(11, 9), (22, 4)]

       """
    implements(IInterfaceIndexer)
    default_field_name = None
    default_interface = None

    def __init__(self, field_name=None, interface=None):
        super(InterfaceIndexingSubscriber, self).__init__()
        if field_name is None and self.default_field_name is None:
            raise ValueError, "Must pass a field_name"
        if field_name is None:
            self._field_name = self.default_field_name
        else:
            self._field_name = field_name
        if interface is None:
            self._interface = self.default_interface
        else:
            self._interface = interface

    field_name = property(lambda self: self._field_name)
    interface = property(lambda self: self._interface)

    def _getValue(self, object):
        if self._interface is not None:
            object = self._interface(object, None)
            if object is None:
                return None

        value = getattr(object, self._field_name, None)
        if value is None:
            return None

        if callable(value):
            try:
                value = value()
            except:
                return None

        return value
        
    def index_doc(self, docid, object):
        value = self._getValue(object)
        return super(InterfaceIndexingSubscriber, self).index_doc(docid, value)
