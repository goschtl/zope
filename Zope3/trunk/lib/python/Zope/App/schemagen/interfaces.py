##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: interfaces.py,v 1.2 2002/12/11 19:07:22 faassen Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class IModuleGenerator:
    def generateModuleSource(schema_name, fields, class_name,
                             schema_history=None):
        """Generate module source containing an interface and class.

        schema_name the name of the schema to generate, fields is the
        fields in the schema (in order), class_name the name of the
        class that implements the schema.  schema_history gives the
        history of the schema up till now. This will be used
        eventually in order to create class transformation code so its
        contents can be updated to a newer version of the schema.
        """

    
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
