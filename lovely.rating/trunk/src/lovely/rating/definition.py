##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Rating definition

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
from zope.schema import fieldproperty
from zope.app.container import contained

from lovely.rating import IRatingDefinition

class RatingDefinition(contained.Contained, persistent.Persistent):
    zope.interface.implements(IRatingDefinition)

    title = fieldproperty.FieldProperty(IRatingDefinition['title'])
    scoreSystem = fieldproperty.FieldProperty(IRatingDefinition['scoreSystem'])
    description = fieldproperty.FieldProperty(IRatingDefinition['description'])

    def __init__(self, title, scoreSystem, description=None):
        self.title = title
        self.scoreSystem = scoreSystem
        if description is not None:
            self.description = description
