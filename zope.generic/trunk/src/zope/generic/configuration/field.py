##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import Attribute
from zope.interface import implements
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.schema import BytesLine
from zope.schema import Dict
from zope.schema import List
from zope.schema import Object
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject

from zope.generic.configuration import INestedConfiguration



class ISubConfiguration(INestedConfiguration, IObject):
    """Mark a single sub configuration field."""

    schema = Attribute('schema',
        _('The interface that defines the fields comprising the sub ' +
          'configuration. The interface must be an IConfigurationType.'))



class SubConfiguration(Object):
    __doc__ = ISubConfiguration.__doc__

    implements(ISubConfiguration)



class ISubConfigurationList(INestedConfiguration, IList):
    """Mark a list of sub configuration objects."""



class SubConfigurationList(List):
    __doc__ = ISubConfigurationList.__doc__

    implements(ISubConfigurationList)

    _type = PersistentList



class ISubConfigurationDict(INestedConfiguration, IDict):
    """Mark a dictionary of sub-configuration bojects."""



class SubConfigurationDict(Dict):
    __doc__ = ISubConfigurationDict.__doc__

    implements(ISubConfigurationDict)

    _type = PersistentDict

    def __init__(self, value_type=None, **kw):
        super(SubConfigurationDict, self).__init__(BytesLine(), value_type, **kw)
