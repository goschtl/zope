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
"""TTW Schema Interfaces

$Id: schema.py,v 1.2 2003/08/16 00:43:34 srichter Exp $
"""
from zope.interface import Interface, Attribute
from zope.interface.interfaces import IInterface
from zope.schema import TextLine
from zope.app.interfaces.container import IAdding
from zope.app.interfaces.component import IInterfaceField, IInterfacesField

class ISchemaUtility(Interface):
    pass

class ISchemaAdding(IAdding):
    pass

class IMutableSchema(IInterface):
    """This object represents an interface/schema that can be edited by
    managing the fields it contains."""

    def getName(name):
        """Get the name of the schema."""

    def setName(name):
        """Set the name of the schema."""

    def addField(name, field):
        """Add a field to schema."""

    def removeField(name):
        """Remove field by name from the schema.

        If the field does not exist, raise an error.
        """

    def renameField(orig_name, target_name):
        """Rename a field.

        If the target_name is already taken, raise an error.
        """

    def insertField(name, field, position):
        """Insert a field with a given name at the specified position.

        If the position does not make sense, i.e. a negative number of a
        number larger than len(self), then an error is raised.
        """

    def moveField(name, position):
        """Move a field (given by its name) to a particular position.

        If the position does not make sense, i.e. a negative number of a
        number larger than len(self), then an error is raised.
        """

class IMutableSchemaField(IInterfaceField):
    """A type of Field that has an IMutableSchema as its value."""

class IMutableSchemasField(IInterfaceField):
    """A type of Field that has a tuple of IMutableSchemas as its value."""


