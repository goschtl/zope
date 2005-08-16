##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id$
"""

from zope.interface import Interface, Attribute

class ITypeRepresentation(Interface):
    """Provide a textual representation of object

    The goal is to have a textual representation (text) that can be
    'eval'ed again so it becomes an object.
    """
    importList = Attribute('List of two-string tuples for use in '
                           'from X import Y')

    text = Attribute('Textual representation of object')


    def getTypes():
        """Return the sequence of types this representation can represent.
        """

class ISchemaSpec(Interface):

    def addField(name, field):
        """Add a field to schema.

        This should be a null operation for instances of the class
        implementing the schema; FieldProperty will provide a default
        for the added field.
        """

    def removeField(name):
        """Remove field from schema.
        """

    def renameField(orig_name, target_name):
        """Rename field.
        """

    def insertField(name, field, position):
        """Insert a field at position.
        """

    def moveField(name, position):
        """Move field to position.
        """

    def generateModuleSource(self):
        pass
