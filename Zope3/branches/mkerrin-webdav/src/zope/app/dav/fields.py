##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""WebDAV-specific fields

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, implements, Attribute
from zope.schema import List, Field, Object, TextLine
from zope.schema.interfaces import IList, IField, IObject
from zope.configuration.fields import GlobalInterface


class IXMLEmptyElementList(IList):
    """XXX - a List field should be used instead of this field.

    Marker interface for the XMLEmptyElementList. This field is very similar
    to the List field but allows users to restricted the values contained
    within the corresponding list.

    It is called this since it is mainly used within WebDAV to restrict the
    values of certain fields.
    """


class XMLEmptyElementList(List):
    implements(IXMLEmptyElementList)

    def __init__(self, value_type = None, unique = True, values = (), **kw):
        """`unique' is False is the base class.
        """
        super(XMLEmptyElementList, self).__init__(value_type, unique, **kw)

        self.values = values

    def _validate(self, value):
        super(XMLEmptyElementList, self)._validate(value)

        if not self.values or not value:
            return

        for item in value:
            if item not in self.values:
                raise WrongContainedType(item)


class IDAVXMLSubProperty(IObject):
    """Sub DAV property.

    schema - specifies the 
    """

    prop_name = TextLine(title = u'Property Name',
                         description = u'Specify the name of a subproperty',
                         required = False)

class DAVXMLSubProperty(Object):
    implements(IDAVXMLSubProperty)

    prop_name = None

    def __init__(self, prop_interface = Interface, prop_name = None, **kw):
        super(DAVXMLSubProperty, self).__init__(**kw)

        self.prop_name = prop_name


class IDAVOpaqueField(IField):
    """ """


class DAVOpaqueField(Field):
    """
    """
    implements(IDAVOpaqueField)
