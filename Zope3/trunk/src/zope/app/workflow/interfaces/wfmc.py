##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for WfMC workflow process definition.

Status: Draft

$Id$
"""
from zope.interface import Interface, Attribute

from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstance
from zope.app.container.interfaces import IContainer

# TODO:
# - Specify all attributes as schema fields where possible
# - Define necessary methods for interfaces

class IWfMCProcessDefinition(IProcessDefinition):
    """WfMC Workflow process definition.
    """

    # will we have packages ??
    # package = Attribute("ref to package")

    processDefinitionHeader = Attribute("ref to pd header")

    redefinableHeader = Attribute("ref to refinable header")

    formalParameters = Attribute("parameters that are interchanged e.g. "
                                 "subflow")

    relevantData = Attribute("wfr data definition")

    participants = Attribute("colletion of participants")

    applications = Attribute("collection of applictations")

    startActivity = Attribute("ref to start activity")

    endActivity = Attribute("ref to end activity")

    activities = Attribute("list activities contained by PD")

    transitions = Attribute("list transitions contained by PD")



class IWfMCProcessDefinitionHeader(Interface):
    """WfMC Workflow process definition header.
    """

    created = Attribute("date of creation")

    description = Attribute("description of package")

    validFrom = Attribute("date the PD is valid from")

    validTo = Attribute("date the PD is valid to")

    limit = Attribute("limit for timemanagement in units of DurationUnit")

    priority = Attribute("priority of PD")

    durationUnit = Attribute("Duration Unit")

    workingTime = Attribute("amount of time, performer of activity needs "
                            "to perform task")

    waitingTime = Attribute("amount of time, needed to prepare performance "
                            "of task")

    duration = Attribute("duration in units")

    timeEstimation = Attribute("estimated time for the process")


class IWfMCProcessDefinitionElement(Interface):
    """WfMC process definition Element."""

    # components usually don't know their id within a container
    # id = Attribute("id of ProcessDefinitionElement")

    # we have to decide how to handle the Extended Attributes
    extendedAttributes = Attribute("list of extended Attributes")


## FormalParameter Declaration

class IWfMCFormalParameter(IContainer):
    """WfMC Formal Parameters Container.
    """

class IWfMCFormalParameter(IWfMCProcessDefinitionElement):
    """WfMC Formal Parameter.
    """

    mode = Attribute("mode: in/out/inout")

    index = Attribute("index of par")

    dataType = Attribute("data type of Parameter")

    description = Attribute("the Parameter Description")


## RelevantData Declaration

class IWfMCRelevantDataContainer(IContainer):
    """WfMC Relevant Data Container.
    """

class IWfMCRelevantData(IWfMCProcessDefinitionElement):
    """WfMC Relevant Data.
    """

    name = Attribute("name of DataField")

    isArray = Attribute("is array ?")

    dataType = Attribute("type of data")

    initialValue = Attribute("initial Value")

    description = Attribute("description of WFRD")


## Application Declaration

class IWfMCApplicationContainer(IContainer):
    """WfMC Application Definition Container.
    """

class IWfMCApplication(IWfMCProcessDefinitionElement):
    """WfMC Application Definition.
    """

    name = Attribute("Name of Application.")

    description = Attribute("Description of Application.")

    formalParameterList = Attribute("Sequence of Formal Parameters.")


## Participant Declaration

class IWfMCParticipantContainer(IContainer):
    """WfMC Participant Definition Container.
    """

class IWfMCParticipant(IWfMCProcessDefinitionElement):
    """WfMC Participant Definition.
    """

    name = Attribute("Name of Participant.")

    type = Attribute("""Type of Participant: RESOURCE_SET/RESOURCE/ROLE/
                        ORGANIZATIONAL_UNIT/HUMAN/SYSTEM""")

    description = Attribute("Description of Participant.")



## Activity

class IWfMCActivityContainer(IContainer):
    """WfMC Activity Container.
    """

class IWfMCActivity(IWfMCProcessDefinitionElement):
    """WfMC Activity.
    """

    # we get get this via acquisition
    # processDefinition = Attribute("ref to PD the activity belongs to")

    name = Attribute("a Activity Name")

    description = Attribute("a description")

    isRoute = Attribute("is this a route Activity")

    startMode = Attribute("how Activity is started (0-Manual/1-Automatic)")

    finishMode = Attribute("how Activity is finished (0-Manual/1-Automatic)")

    performer = Attribute("link to workflow participant (may be expression)")

    implementation = Attribute("if not Route-Activity: mandatory "
                               "(no/tool+/subflow/loop)")

    instantiation = Attribute("capability: once/multiple times")

    priority = Attribute("priority of Activity")

    cost = Attribute("average cost")

    workingTime = Attribute("amount of time, performer of activity needs "
                            "to perform task")

    waitingTime = Attribute("amount of time, needed to prepare performance "
                            "of task")

    duration = Attribute("duration of activity")

    limit = Attribute("limit in costUnits")

    icon = Attribute("icon of activity")

    documentation = Attribute("documentation")

    splitMode = Attribute("split Mode (and/xor)")

    joinMode = Attribute("join Mode (and/xor)")

    inlineBlock = Attribute("inline Block definition")



class IWfMCImplementation(IWfMCProcessDefinitionElement):
    """WfMC Implementation Definition.

    is referenced by Activity Attribute: implementation.
    """

    type = Attribute("Type of Implementation: NO/SUBFLOW/TOOL")


class IWfMCSubflow(IWfMCImplementation):
    """WfMC Implementation Subflow.
    """

    name = Attribute("Name of Subflow to start.")

    execution = Attribute("Type of Execution: Asynchr/synchr.")

    actualParameterList = Attribute("Sequence of ActualParameters with those "
                                    "the new Instance is initialized and "
                                    "whose are returned.")


class IWfMCTool(IWfMCImplementation):
    """WfMC Implementation Subflow.
    """

    name = Attribute("Name of Application/Procedure to invoke "
                     "(Application Declaration).")

    type = Attribute("Type of Tool: APPLICATION/PROCEDURE.")

    description = Attribute("Description of Tool.")

    actualParameterList = Attribute("Sequence of ActualParameters with those "
                                    "the new Instance is initialized and "
                                    "whose are returned.")



## Transition

class IWfMCCondition(Interface):
    """WfMC Condition.
    """

    type = Attribute("Type of Condition: CONDITION/OTHERWISE")

    expression = Attribute("Expression to evaluate.")


class IWfMCTransitionContainer(IContainer):
    """WfMC Transition Container.
    """

class IWfMCTransition(IWfMCProcessDefinitionElement):
    """WfMC Transition.
    """

    name = Attribute("Name of Transition.")

    condition = Attribute("ref to Condition.")

    fromActivityId = Attribute("Id of FromActivity.")

    toActivityId = Attribute("Id of ToActivity.")


class IWfMCProcessInstanceData(Interface):
    """WfMC ProcessInstance Data.

    This is a base interfaces that gets extended dynamically when creating a
    ProcessInstance from the relevantData Spec.
    """


class IWfMCProcessInstance(IProcessInstance):
    """WfMC Workflow process instance.
    """

    processDefinitionId = Attribute("Id of ProcessDefinition.")

    name = Attribute("Name of ProcessInstance.")

    creationTime = Attribute("Creation Time of ProcessInstance.")

    activityInstances = Attribute("ref to ActivityInstanceContainer.")

    data = Attribute("WorkflowRelevant Data (instance, not definition.)")

    # We might need an actual Participantlist for the implementation.


class IWfMCActivityInstanceContainer(IContainer):
    """WfMC ActivityInstance Container.
    """

class IWfMCActivityInstance(Interface):
    """WfMC Workflow activity instance.
    """

    activityId = Attribute("Id of Activity.")

    name = Attribute("Name of ActivityInstance.")

    creationTime = Attribute("Creation Time of ActivityInstance.")

    status = Attribute("Status of ActivityInstance.")

    priority = Attribute("Priority of ActivityInstance (initialized from "
                         "Activity).")

    workitems = Attribute("ref to WorkitemContainer.")

    # participants = Attribute("Sequence of assigned Participants.")

class IWfMCWorkitemContainer(IContainer):
    """WfMC Workitem Container.
    """

class IWfMCWorkitem(Interface):
    """WfMC Workflow  instance.
    """

    status = Attribute("Status of Workitem.")

    priority = Attribute("Priority of Workitem.")

    participant = Attribute("Participant that is assigned to do this item "
                            "of Work.")

