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

from zope.app.event.objectevent import ObjectEvent
from zope.interface import implements

from zope.generic.configuration import IObjectConfiguredEvent
from zope.generic.configuration import IConfigurationModificationDescription



class Configuration(object) :
    """Describes a single modified configuration.

    A possible configuration schema:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IMyConfiguration(Interface):
        ...     my = TextLine(title=u'My')

    Check interface implementation:
        
        >>> description = Configuration(IMyConfiguration, {'my': u'Bla'})

        >>> IConfigurationModificationDescription.providedBy(description)
        True

        >>> description.keyface == IMyConfiguration
        True

        >>> 'my' in description.data
        True
        >>> description.data.get('my')
        u'Bla'

    If no data argument is set, the data attribute will be set to an empty
    dict, which implies that the configuration was deleted:

        >>> description = Configuration(IMyConfiguration)
        >>> description.keyface == IMyConfiguration
        True

        >>> description.data
        {}

    """

    implements(IConfigurationModificationDescription)

    def __init__(self, keyface, data=None) :
        self.keyface = keyface
        if data is not None:
            self.data = data

        else:
            self.data = {}



class ObjectConfiguredEvent(ObjectEvent):
    """An object's configurations has been modified.
        
    A possible configuration schema:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
                
        >>> class IMyConfiguration(Interface):
        ...     my = TextLine(title=u'My')
        
        >>> class IYourConfiguration(Interface):
        ...     your = TextLine(title=u'Your')
         
        >>> class IRegularInterface(Interface):
        ...    pass
 
    A possible event:
 
        >>> descriptions = []
        >>> descriptions.append(Configuration(IMyConfiguration, {'my': u'Bla'}))
        >>> descriptions.append(Configuration(IYourConfiguration))
        >>> from zope.app.event.objectevent import Attributes
        >>> descriptions.append(Attributes(IRegularInterface))
        >>> context = object()
        >>> event = ObjectConfiguredEvent(context, *descriptions)

    There are two convenience function to introspect configuration modifications
    specifically:

        >>> len(event.descriptions) is 3
        True

        >>> items = event.items()
        >>> len(items) is 2
        True
        >>> [(interface.__name__, data) for interface, data in items]
        [('IMyConfiguration', {'my': u'Bla'}), ('IYourConfiguration', {})]

        >>> event.get(IMyConfiguration)
        {'my': u'Bla'}

        >>> event.get(IYourConfiguration)
        {}

        >>> event.get(IRegularInterface, 'default')
        'default'
    """

    implements(IObjectConfiguredEvent)

    def __init__(self, object, *descriptions):
        super(ObjectConfiguredEvent, self).__init__(object) 
        self.descriptions = descriptions

    def items(self):
        return [(d.keyface, d.data) for d in self.descriptions 
                   if IConfigurationModificationDescription.providedBy(d)]

    def get(self, keyface, default=None):
        result = [d.data for d in self.descriptions 
                   if IConfigurationModificationDescription.providedBy(d) and d.keyface is keyface]
        if result:
            return result[0]

        else:
            return default
