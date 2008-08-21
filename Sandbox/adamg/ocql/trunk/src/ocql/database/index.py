# -*- coding: UTF-8 -*-

"""Special index to collect all objects providing an interface

$Id$
"""

#TODO: not optimal, uses FieldIndex with a value of always 1

#TODO: later: keep a count of objects stored for len() and optimization

import zope.index.field
import zope.interface
import zope.schema

from zope.i18nmessageid import ZopeMessageFactory as _

import zope.app.container.contained
import zope.app.catalog.attribute
import zope.app.catalog.interfaces

class IAllIndex(zope.interface.Interface):
    """I index objects by first adapting them to an interface, then
       retrieving a field on the adapted object.
    """

    interface = zope.schema.Choice(
        title=_(u"Interface"),
        description=_(u"Objects will be adapted to this interface"),
        vocabulary="Interfaces",
        required=False,
        )


class IAllMixinIndex(IAllIndex,
                  zope.app.catalog.interfaces.ICatalogIndex):
    """Interface-based catalog index
    """

class AllMixinIndex(object):
    """Index interface-defined attributes

       Mixin for indexing all objects providing a particular interface.

       The class is meant to be mixed with a base class that defines an
       index_doc method:

         >>> class BaseIndex(object):
         ...     def __init__(self):
         ...         self.data = []
         ...     def index_doc(self, id, value):
         ...         self.data.append((id, value))

         >>> class Index(AllMixinIndex, BaseIndex):
         ...     pass

         Let's setup two interfaces with classes to test:

         >>> from zope.interface import Interface
         >>> from zope.interface import implements

         >>> class I1(Interface):
         ...     pass

         >>> class I2(Interface):
         ...     pass

         >>> class Data1:
         ...     implements(I1)
         ...     def __init__(self, v):
         ...         self.x = v

         >>> class Data2:
         ...     implements(I2)
         ...     def __init__(self, v):
         ...         self.x = v

         >>> class Data3:
         ...     implements(I1, I2)
         ...     def __init__(self, v):
         ...         self.x = v

         Our index will index all objects providing I1:

         >>> index1 = Index(interface=I1)

         Those two provide it, they get indexed:

         >>> index1.index_doc(11, Data1(1))
         >>> index1.index_doc(22, Data1(2))
         >>> index1.data
         [(11, 1), (22, 1)]

         Those two provide I2, they DONT get indexed:

         >>> index1.index_doc(110, Data2(21))
         >>> index1.index_doc(220, Data2(22))
         >>> index1.data
         [(11, 1), (22, 1)]

         Those two provide also it, they get indexed:

         >>> index1.index_doc(1100, Data3(21))
         >>> index1.index_doc(2200, Data3(22))
         >>> index1.data
         [(11, 1), (22, 1), (1100, 1), (2200, 1)]


       """

    zope.interface.implements(IAllMixinIndex)

    default_interface = None

    def __init__(self, interface=None,
                 *args, **kwargs):
        #we don't care about field_name and field_callable
        super(AllMixinIndex, self).__init__(*args, **kwargs)
        if interface is None:
            self.interface = self.default_interface
        else:
            self.interface = interface

        if self.interface is None:
            raise ValueError("Must pass an interface")

    def index_doc(self, docid, object):
        if not self.interface.providedBy(object):
            return None

        return super(AllMixinIndex, self).index_doc(docid, 1)



class AllIndex(AllMixinIndex,
                 zope.index.field.FieldIndex,
                 zope.app.container.contained.Contained):

    zope.interface.implements(IAllIndex)
