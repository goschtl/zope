##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

"""Transition event subscribers

$Id: $
"""

from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager

from zope.app.workflow.stateful.interfaces import IStatefulPIAdapter

def transitionUserTriggeredSubscriber(event):
    """Transition User Triggered Subscriber

    Subscriber to event that occurs when the user submit through a
    TransitionChangeFormView

    This is the actual subscriber responsible to trigger the transition
    """
    process_instance_adapted = IStatefulPIAdapter(event.object)
    if process_instance_adapted is not None:
        try:
            process_instance_adapted.fireTransition(event.form_action, event)
        except KeyError:
            raise str("Transition %s is not allowed" %(event.form_action))
    else:
        raise 'No adapter IStatefulPIAdapter found for on %s'%(str(event.object))
    return 1

def _getCreator(obj):
    """Returns the creator of the object
    """
    # XXX use IAnotation instead
    DCkey = "zope.app.dublincore.ZopeDublinCore"
    annos = obj.__annotations__
    return annos[DCkey]['Creator'][0]

def afterTransitionEventSubscriber(event):
    """After Transition Event Subscriber

    Subscriber to the event that occurs after the transition has been fired.

    It will be resposible for the grants.

    This subscriber can be replaced by another one to change the policy.
    """

    # XXX this is specific to a given workflow. Let's see how to cope with that
    # and fix it. Probably we need to put this mapping on the state itself

    # Get event properties
    transition = event.transition
    transition_name = transition.__name__
    context = event.context

    # ipm
    ipm = IRolePermissionManager(context)
    ppm = IPrincipalPermissionManager(context)

    # transition.getProcessDefinition()
    # destination_state = pdefinition.getState(destination_state_name)

    destination_state_name = transition.destinationState

    if destination_state_name == "INITIAL":

        #
        # We don't do anything in here
        # the mapping is the actual mapping at creation time
        # It's then depending on the context
        #

        print "::afterTransitionEventSubscriber():: destination is private state"

        creator = _getCreator(context)

        if transition_name in ('reject', 'retract'):
            ppm.grantPermissionToPrincipal('zope.ManageContent', creator)
        elif transition_name == 'unpublish':
            ppm.denyPermissionToPrincipal('zope.View', 'zope.anybody')
            ppm.grantPermissionToPrincipal('zope.ManageContent', creator)

    elif destination_state_name == "pending":

        #
        # Here, we remove the 'Manage Content' to the Owner
        # add Mange Content and View to the 'Content Reviewer' Role
        #

        print "::afterTransitionEventSubscriber():: destination is pending state"

        creator = _getCreator(context)
        ppm.denyPermissionToPrincipal('zope.ManageContent', creator)

    elif destination_state_name == "published":

        #
        # Here, we simply add the 'View' permission to the nobody principal
        # since it's published
        #

        print "::afterTransitionEventSubscriber():: destination is published state"
        ppm.grantPermissionToPrincipal('zope.View', 'zope.anybody')

    else:
        pass

def transitionAddedEventSubscriber(event):
    """Transition added event subscriber
    """
    obj = event.object
    state_adapted = ITransitionActionAdapter(obj)
