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

from zope.component import factory
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.interface import alsoProvides

from zope.generic.configuration.api import parameterToConfiguration
from zope.generic.configuration.api import configuratonToDict
from zope.generic.directlyprovides.api import updateDirectlyProvided
from zope.generic.informationprovider.api import getInformationProvider
from zope.generic.informationprovider.api import provideInformation
from zope.generic.informationprovider.api import queryInformation
from zope.generic.face import IAttributeFaced
from zope.generic.face import IProvidesAttributeFaced
from zope.generic.face.api import Face
from zope.generic.operation import INoParameter
from zope.generic.operation import IOperationConfiguration
from zope.generic.operation import IUndefinedParameter
        


class Factory(factory.Factory, Face):
    """Key-interface-based factory implementation.

    First we declare an key interface:

        >>> from zope.interface import Interface

        >>> class IMyInstance(Interface):
        ...     pass

    Second we need an implementation class. There are different possible ways.
    We try first the easiest one:

        >>> class Simple(object):
        ...    pass

        >>> from zope.generic.factory.factory import Factory

        >>> f = Factory(Simple, IMyInstance)
        >>> f()
        <example.Simple object at ...>
        
        >>> f.title
        u''
        >>> f.description
        u''

        >>> f('wrong')
        Traceback (most recent call last):
        ...
        TypeError: default __new__ takes no parameters

    We can provide the key interface during the creation:

        >>> f = Factory(Simple, IMyInstance, providesFace=True)
        >>> IMyInstance.providedBy(f())
        True

    If the class does implement IAttributeFaced the __keyface__
    attribute is set too:

        >>> from zope.generic.face import IAttributeFaced

        >>> class SimpleKeyFaced(object):
        ...    interface.implements(IAttributeFaced)

        >>> f = Factory(SimpleKeyFaced, IMyInstance, providesFace=True)
        >>> IMyInstance.providedBy(f())
        True
        >>> f().__keyface__ is IMyInstance
        True

    We can notify an ObjectCreatedEvent for created instance:

        >>> from zope.component.eventtesting import getEvents, clearEvents
        >>> clearEvents()

        >>> f = Factory(Simple, IMyInstance, notifyCreated=True)
        >>> instance = f()
        
        >>> events = getEvents()
        >>> len(events)
        1
        >>> events.pop().object is instance
        True

    There are further features but to use them we have to register an
    an IFactory information provider including an
    IOperationConfiguration:

        >>> def init_handler(context, *pos, **kws):
        ...    print 'initializing'

        >>> from zope.generic.configuration.api import ConfigurationData
        >>> from zope.generic.operation import IOperationConfiguration
        >>> from zope.generic.operation.api import Operation

        >>> my_factory={'operation': Operation(init_handler)}

        >>> registerDirective('''
        ... <generic:informationProvider
        ...     keyface="example.IMyInstance"
        ...     >
        ...    <information
        ...       keyface="zope.generic.operation.IOperationConfiguration"
        ...       configuration="example.my_factory"
        ...       />
        ... </generic:informationProvider>
        ... ''')

        >>> f = Factory(Simple, IMyInstance, useConfig=True)
        >>> f()
        initializing
        <example.Simple object at ...>
        
        >>> f('wrong')
        Traceback (most recent call last):
        ...
        TypeError: This factory takes no parameters


    If we like to provide parameter we have to declare them by an input
    configuration:

        >>> from zope.schema import TextLine

        >>> class SimpleKeyFacedWithParameter(object):
        ...    interface.implements(IAttributeFaced)
        ...    def __init__(self, a, b, c):
        ...        print '__init__:', 'a=',a ,', b=', b, ', c=', c

        >>> class IMyParameter(Interface):
        ...    a = TextLine()
        ...    b = TextLine(required=False)
        ...    c = TextLine(required=False, default=u'c default')

        >>> registerDirective('''
        ... <generic:interface
        ...     interface="example.IMyParameter"
        ...     type="zope.generic.configuration.IConfigurationType"
        ...     />
        ... ''') 

        >>> my_factory={'operation': Operation(init_handler), 'input': IMyParameter}

        >>> registerDirective('''
        ... <generic:informationProvider
        ...     keyface="example.IMyInstance"
        ...     >
        ...    <information
        ...       keyface="zope.generic.operation.IOperationConfiguration"
        ...       configuration="example.my_factory"
        ...       />
        ... </generic:informationProvider>
        ... ''')

        >>> f = Factory(SimpleKeyFacedWithParameter, IMyInstance, useConfig=True)
        >>> f(u'a bla bla')
        __init__: a= a bla bla , b= None , c= c default
        initializing
        <example.SimpleKeyFacedWithParameter object at ...>

    We can ignore the factory configuration fully by mode=0:

        >>> f = Factory(SimpleKeyFacedWithParameter, IMyInstance, useConfig=False)
        >>> f(u'a bla bla')
        Traceback (most recent call last):
         ...
        TypeError: __init__() takes exactly 4 arguments (2 given)

    Last but not least we can store the arguments directly as configuration. 
    Such an configuration can be retrieved later on using the queryInformation
    function:

        >>> from zope.generic.informationprovider import IAttributeInformable

        >>> class SimpleConfigurable(object):
        ...    interface.implements(IAttributeInformable, IAttributeFaced)
        ...    def __init__(self, a, b, c):
        ...        print '__init__:', 'a=',a ,', b=', b, ', c=', c

        >>> f = Factory(SimpleConfigurable, IMyInstance, storeInput=True, useConfig=True)
        >>> instance = f(u'a bla')
        __init__: a= a bla , b= None , c= c default
        initializing
        
        >>> from zope.generic.informationprovider.api import queryInformation
        
        >>> config = queryInformation(IMyParameter, instance)
        >>> config.a, config.b, config.c
        (u'a bla', None, u'c default')

    """

    def __init__(self, callable, __keyface__, providesFace=False, 
                 storeInput=False, notifyCreated=False, 
                 title=u'', description=u'', useConfig=False):

        super(Factory, self).__init__(callable, title, description, interfaces=(__keyface__,))

        # essentials
        self.__keyface__ = __keyface__
        self.__provideFace = providesFace
        self.__storeInput = storeInput
        self.__notifyCreated = notifyCreated
        # this assigns that there will be no configuration within an informatio provider
        if useConfig is False:
            self.__dict__['_Factory__config'] = None

    def __call__(self, *pos, **kws):
        """Create instance."""
        config = self.__config
        # handle declared callables
        new_kws = None
        if config and config.input != IUndefinedParameter:
            # callables with no parameter
            if config.input == INoParameter:
                if kws or pos:
                    raise TypeError('This factory takes no parameters')

                instance = self._callable()

            # callables with defined parameters
            else:
                new_kws = configuratonToDict(parameterToConfiguration(config.input, *pos, **kws), all=True)
                instance = self._callable(**new_kws)

        # handle undeclared ones
        else:
            instance = self._callable(*pos, **kws)

        # provide key interface
        if self.__provideFace:
            if not self.keyface.providedBy(instance):
                if IProvidesAttributeFaced.providedBy(instance):
                    instance.__dict__['__keyface__'] = self.keyface
                    updateDirectlyProvided(instance, self.keyface)

                elif IAttributeFaced.providedBy(instance):
                    instance.__dict__['__keyface__'] = self.keyface
                    alsoProvides(instance, self.keyface)

                else:
                    alsoProvides(instance, self.keyface)

        # store input configuration
        if self.__storeInput and config:
            input = config.input
            if input:
                if new_kws:
                    configuration = parameterToConfiguration(input, **new_kws)

                else:
                    configuration = parameterToConfiguration(input, *pos, **kws)

                provideInformation(input, configuration, instance)

        # invoke initializer operations
        operation = getattr(config, 'operation', None)
        if operation:
            if new_kws:
                config.operation(instance, **new_kws)

            else:
                config.operation(instance, *pos, **kws)

        # notify created object
        if self.__notifyCreated:
            notify(ObjectCreatedEvent(instance))

        return instance

    @property
    def __config(self):
        if '_Factory__config' not in self.__dict__:
            try:
                provider = getInformationProvider(self.keyface)
                self.__dict__['_Factory__config'] = queryInformation(IOperationConfiguration, provider)

            except:
                self.__dict__['_Factory__config'] = None


        return self.__dict__['_Factory__config']
