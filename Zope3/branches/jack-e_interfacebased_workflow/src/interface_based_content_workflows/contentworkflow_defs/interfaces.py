from zope import interface

#
# Interface represnting the process itself
#

class IContentWorkflowDefinition(interface.Interface):
    """Content Process Definition Interface

    Interface representing the the content process definition for Z3 content
    objects
    """

    # XXX we are not suppposed to be in need of that
    # event subscriber needs to find it to find the
    __processdefinition_name__ = interface.Attribute('Process Definition Name')


#
# Interfaces representing states
#

class IStateContentWorkflowPrivate(IContentWorkflowDefinition):
    """ Private State for used by content workflow
    """

class IStateContentWorkflowPending(IContentWorkflowDefinition):
    """ Pending State for used by content workflow
    """

class IStateContentWorkflowPublished(IContentWorkflowDefinition):
    """ Published State for used by content workflow
    """
