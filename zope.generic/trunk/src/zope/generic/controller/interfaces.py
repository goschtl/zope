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

from zope.app.annotation import IAnnotations
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Object
from zope.schema import Tuple

from zope.generic.component import IInterfaceKey
from zope.generic.configuration import IConfiguraitons
from zope.generic.type import ITypeType



class IHandler(Interface):
    """ """
    def __call__(controller, event=None):
        """Handle the controller's context."""



class IHandlerConfiguration(Interface):
    """Tell the controller which handler should be invoked."""

    preHandlers = Tuple(title=_('Pre-Handlers'),
        description=_('Handler that should be invoked before the Super-Call.'),
        required=False,
        default=(),
        value_type=Object(schema=IHandler))

    postHandlers = Tuple(title=_('Post-Handlers'),
        description=_('Handler that should be invoked after the Super-Call.'),
        required=False,
        default=(),
        value_type=Object(schema=IHandler))

    callSupers = Bool(title=_('Call Super'),
        description=_('Should the supers be called?'),
        default=False)

class IInitializeConfiguration(IHandlerConfiguration):
    """Configuration for initializer handlers."""

class IModifyConfiguration(IHandlerConfiguration):
    """Configuration for adder handlers."""

class IAddConfiguration(IHandlerConfiguration):
    """Configuration for adder handlers."""


class IMoveConfiguration(IHandlerConfiguration):
    """Configuration for adder handlers."""


class IRemoveConfiguration(IHandlerConfiguration):
    """Configuration for adder handlers."""


class IUpdateConfiguration(IHandlerConfiguration):
    """Configuration for adder handlers."""

alsoProvides(IControllerConfiguration, IConfigurationType)


class IListener(IInterfaceKey):
    """Listen as a subscriber to events defined by the interface."""

    def __call__(component, event):
        """Redirect the call to the controller.
        name = toDottedName()
        controller = IController(component, event)

            
        
        
        
        """



class IController(Interface):
    """Apply dedicated handlers to a component context.

    The controller should invoke the handler in a object-oriented manner.

    Object-orientation provides an overwrites-mechanism within an inheritance
    hierarchy. There are to possibilities for an certain class of that
    inheritance tree to be invoke by a call:
        
        def method(x):
            # before the supers will be called
            any_pre_super_call_procedures(x)
            # super call
            super_call(x)
            # after the supers were called.
            any_post_super_call_procedures(x)
    
    We can observe an generalizing information flow from specialized to 
    generalized (preSuperCall) and an specializing information flow 
    from generalized to specialized (postSuperCall). an configurator will
    """


    context = Object(title=_('Context'),
        description=_('The context that should be configured.'),
        default=True)

    def __call__(event=None):
        """Apply the handlers.
        
        First invoke the pre-handlers defined by the interface-inheritance order
        of the interface-key marker as listed in inface-key.flattened() call if 
        the interface provides ITypeType.
        
        Second invoke the post-handlers in the inverse order.

        id = ITyped(component).interface
        if callSupers:
            interfaces = [iface for iface in id.flattened if ITypeType.providedBy(iface)]
        else:
            interfaces = [id]
        
        for iface in interfaces:
            getAdapter(component, [IController], name=toDottedName(id))

        """

    configurations = Object(
        title=_('Configurations'),
        description=_('The configurations of the component.'),
        required=False,
        readonly=True,
        schema=IConfigurations)

    annotations = Object(
        title=_('Annotations'),
        description=_('The annotations of the component.'),
        required=False,
        readonly=True,
        schema=IAnnotations)
