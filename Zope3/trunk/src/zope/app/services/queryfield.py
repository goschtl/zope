##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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

$Id: queryfield.py,v 1.2 2003/02/11 15:59:56 sidnei Exp $
"""
from zope.app.services.field import locateComponent
from zope.schema import Tuple
from zope.schema.interfaces import ValidationError
from zope.component import getAdapter
from zope.interface.implements import implements
# See end of file for further imports

class QueryProcessorsField(Tuple):

    def __init__(self, default=(), *args, **kw):
        super(QueryProcessorsField, self).__init__(default=default,
                                                   *args, **kw)

    def _validate(self, value):
        super(QueryProcessorsField, self)._validate(value)
        context = self.context
        for location, adaptername in value:
            component = locateComponent(location, context, IQueryProcessable)
            processor = getAdapter(component, IQueryProcessor,
                                   context=context, name=adaptername)
            if processor is None:
                if name:
                    message = 'No IQueryProcessor adapter named "%s" found'
                else:
                    message = 'No IQueryProcessor adapter found'
                raise ValidationError(message, location)



# Imported here to avoid circular imports
from zope.app.interfaces.services.query import IQueryProcessorsField
from zope.app.interfaces.services.query import IQueryProcessable
from zope.app.interfaces.services.query import IQueryProcessor
implements(QueryProcessorsField, IQueryProcessorsField)

