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
"""

$Id: PropertyFieldAdapter.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from IPropertyFieldAdapter import IPropertyFieldAdapter
from Zope.App.Formulator.Errors import ValidationError

class PropertyFieldAdapter:
    """ """

    __implements__ = IPropertyFieldAdapter


    def __init__(self, context):
        """ """
        self.context = context


    def setPropertyInContext(self, value):
        """ """
        field = self.context
        method = getattr(field.context,
                        'set'+field.id[0].capitalize()+field.id[1:], None)
        apply(method, (value,))


    def getPropertyInContext(self):
        """ """
        field = self.context
        method = getattr(field.context,
                        'get'+field.id[0].capitalize()+field.id[1:], None)
        return apply(method, ())
