##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
from Zope.ComponentArchitecture.IContextDependent import IContextDependent

class IField(IContextDependent):
    """
    """

    def getValidator():
        """Return the validator of this field."""


    def hasValue(id):
        """Return true if the field defines such a value.
        """


    def getValue(id):
        """Get value for id."""


    def getOverride(id):
        """Get override method for id (not wrapped)."""


    def getTales(id):
        """Get tales expression method for id."""
    

    def isRequired():
        """Check whether this field is required (utility function)
        """    


    def getErrorNames():
        """Get error messages.
        """


    def isTALESAvailable():
        """Return true only if TALES is available.
        """
