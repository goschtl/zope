##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
""" Web-configurable workflow.

$Id$
"""

dcworkflow_globals = globals()

def initialize(context):

    from Products.CMFCore.utils import registerIcon

    import DCWorkflow
    import States
    import Transitions
    import Variables
    import Worklists
    import Scripts
    import Default
    
    context.registerHelp(directory='help')
    context.registerHelpTitle('DCWorkflow')
    
    registerIcon(DCWorkflow.DCWorkflowDefinition,
                 'images/workflow.gif', dcworkflow_globals)
    registerIcon(States.States,
                 'images/state.gif', dcworkflow_globals)
    States.StateDefinition.icon = States.States.icon
    registerIcon(Transitions.Transitions,
                 'images/transition.gif', dcworkflow_globals)
    Transitions.TransitionDefinition.icon = Transitions.Transitions.icon
    registerIcon(Variables.Variables,
                 'images/variable.gif', dcworkflow_globals)
    Variables.VariableDefinition.icon = Variables.Variables.icon
    registerIcon(Worklists.Worklists,
                 'images/worklist.gif', dcworkflow_globals)
    Worklists.WorklistDefinition.icon = Worklists.Worklists.icon
    registerIcon(Scripts.Scripts,
                 'images/script.gif', dcworkflow_globals)
