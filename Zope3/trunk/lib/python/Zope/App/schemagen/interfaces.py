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

$Id: interfaces.py,v 1.1 2002/12/11 16:11:14 faassen Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class ITypeRepresentation(Interface):

    importList = Attribute('List of two-string tuples for use in '
                           'from X import Y')

    text = Attribute('Textual representation of object')


    def getTypes():
        """Return the sequence of types this representation can represent.
        """
