from Products.CMFCore.WorkflowTool import addWorkflowFactory

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def setupCollector_issue_workflow(wf):
    "..."
    wf.setProperties(title='Collector issue workflow')

    for s in ['Resolved', 'Deferred', 'Pending_confidential', 'Testing', 'Rejected', 'Accepted_confidential', 'Testing_confidential', 'New', 'Wontfix', 'Accepted', 'Pending']:
        wf.states.addState(s)
    for t in ['defer', 'reject-test_confidential', 'staffed_confidential', 'restrict_pending', 'wontfix', 'test_confidential', 'staffed', 'new_issue', 'unrestrict_accepted', 'resubmit', 'reject', 'test', 'new_issue_confidential', 'resign', 'restrict_accepted', 'accept', 'abandoned_confidential', 'abandoned', 'resolve', 'reject-test', 'unrestrict_pending', 'request', 'assign', 'accept_confidential', 'assign_confidential']:
        wf.transitions.addTransition(t)
    for v in ['requested', 'confidential', 'assigned_to']:
        wf.variables.addVariable(v)
    for l in []:
        wf.worklists.addWorklist(l)
    for p in ('Access contents information', 'View', 'Edit collector issue', 'Add collector issue artifact', 'Support collector issue'):
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('New')

    ## States initialization
    sdef = wf.states['Resolved']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'assign', 'reject', 'resign', 'resubmit'))
    sdef.setPermission('Access contents information', 1, ['Anonymous'])
    sdef.setPermission('View', 1, ['Anonymous'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Deferred']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'accept_confidential', 'assign', 'assign_confidential', 'reject', 'resolve', 'resubmit', 'wontfix'))
    sdef.setPermission('Access contents information', 1, ['Anonymous'])
    sdef.setPermission('View', 1, ['Anonymous'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Pending_confidential']
    sdef.setProperties(title="""""",
                       transitions=('accept_confidential', 'assign_confidential', 'reject', 'request', 'resolve', 'staffed_confidential', 'test_confidential', 'unrestrict_pending', 'wontfix'))
    sdef.setPermission('Access contents information', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('View', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Testing']
    sdef.setProperties(title="""""",
                       transitions=('assign', 'reject-test', 'resolve'))
    sdef.setPermission('Access contents information', 1, [])
    sdef.setPermission('View', 1, [])
    sdef.setPermission('Edit collector issue', 1, [])
    sdef.setPermission('Add collector issue artifact', 1, [])
    sdef.setPermission('Support collector issue', 1, [])

    sdef = wf.states['Rejected']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'accept_confidential', 'assign', 'defer', 'resolve', 'resubmit', 'wontfix'))
    sdef.setPermission('Access contents information', 1, ['Anonymous'])
    sdef.setPermission('View', 1, ['Anonymous'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Accepted_confidential']
    sdef.setProperties(title="""""",
                       transitions=('abandoned_confidential', 'accept_confidential', 'assign_confidential', 'reject', 'resign', 'resolve', 'test_confidential', 'unrestrict_accepted', 'wontfix'))
    sdef.setPermission('Access contents information', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('View', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Testing_confidential']
    sdef.setProperties(title="""""",
                       transitions=('assign_confidential', 'reject-test_confidential', 'resolve'))
    sdef.setPermission('Access contents information', 1, [])
    sdef.setPermission('View', 1, [])
    sdef.setPermission('Edit collector issue', 1, [])
    sdef.setPermission('Add collector issue artifact', 1, [])
    sdef.setPermission('Support collector issue', 1, [])

    sdef = wf.states['New']
    sdef.setProperties(title="""""",
                       transitions=('new_issue', 'new_issue_confidential', 'request'))
    sdef.setPermission('Access contents information', 1, [])
    sdef.setPermission('View', 1, [])
    sdef.setPermission('Edit collector issue', 1, [])
    sdef.setPermission('Add collector issue artifact', 1, [])
    sdef.setPermission('Support collector issue', 1, [])

    sdef = wf.states['Wontfix']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'accept_confidential', 'assign', 'defer', 'resolve', 'resubmit'))
    sdef.setPermission('Access contents information', 1, [])
    sdef.setPermission('View', 1, [])
    sdef.setPermission('Edit collector issue', 1, [])
    sdef.setPermission('Add collector issue artifact', 1, [])
    sdef.setPermission('Support collector issue', 1, [])

    sdef = wf.states['Accepted']
    sdef.setProperties(title="""""",
                       transitions=('abandoned', 'accept', 'assign', 'defer', 'reject', 'resign', 'resolve', 'restrict_accepted', 'test', 'wontfix'))
    sdef.setPermission('Access contents information', 1, ['Anonymous'])
    sdef.setPermission('View', 1, ['Anonymous'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])

    sdef = wf.states['Pending']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'assign', 'defer', 'reject', 'request', 'resolve', 'restrict_pending', 'staffed', 'test', 'wontfix'))
    sdef.setPermission('Access contents information', 1, ['Anonymous'])
    sdef.setPermission('View', 1, ['Anonymous'])
    sdef.setPermission('Edit collector issue', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('Add collector issue artifact', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Support collector issue', 0, ['Manager', 'Reviewer'])


    ## Transitions initialization
    tdef = wf.transitions['defer']
    tdef.setProperties(title="""""",
                       new_state_id="""Deferred""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""defer""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'not: status/confidential', 'guard_permissions': 'Support collector issue'},
                       )

    tdef = wf.transitions['reject-test_confidential']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""reject-test_confidential""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    tdef = wf.transitions['staffed_confidential']
    tdef.setProperties(title="""(Pending) issue with staff becomes (accepted)""",
                       new_state_id="""Accepted_confidential""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_expr': "python: status['confidential'] and status['assigned_to']"},
                       )

    tdef = wf.transitions['restrict_pending']
    tdef.setProperties(title="""Make confidential""",
                       new_state_id="""Pending_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""restrict_pending""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 1')

    tdef = wf.transitions['wontfix']
    tdef.setProperties(title="""Assert that the issue won't be fixed""",
                       new_state_id="""Wontfix""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""wontfix""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['test_confidential']
    tdef.setProperties(title="""Assign to client for testing""",
                       new_state_id="""Testing_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""test_confidential""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    tdef = wf.transitions['staffed']
    tdef.setProperties(title="""Pending issue with staff becomes accepted""",
                       new_state_id="""Accepted""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: not status['confidential'] and status['assigned_to']"},
                       )

    tdef = wf.transitions['new_issue']
    tdef.setProperties(title="""Situate new non-security-related issues""",
                       new_state_id="""Pending""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'not: here/security_related'},
                       )
    tdef.addVariable(id='requested', text='python: 0')
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['unrestrict_accepted']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""unrestrict_accepted""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['resubmit']
    tdef.setProperties(title="""""",
                       new_state_id="""New""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""resubmit""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )

    tdef = wf.transitions['reject']
    tdef.setProperties(title="""""",
                       new_state_id="""Rejected""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""reject""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['test']
    tdef.setProperties(title="""""",
                       new_state_id="""Testing""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""test""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    tdef = wf.transitions['new_issue_confidential']
    tdef.setProperties(title="""Situate new security-related issues""",
                       new_state_id="""Pending_confidential""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'here/security_related'},
                       )
    tdef.addVariable(id='requested', text='python: 0')
    tdef.addVariable(id='confidential', text='python: 1')

    tdef = wf.transitions['resign']
    tdef.setProperties(title="""""",
                       new_state_id="""""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""resign""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'here/is_assigned', 'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple([ assignee for assignee in here.assigned_to() if  assignee != state_change.kwargs['username'] ])")

    tdef = wf.transitions['restrict_accepted']
    tdef.setProperties(title="""Make confidential""",
                       new_state_id="""Accepted_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""restrict_accepted""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 1')

    tdef = wf.transitions['accept']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""accept""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: not status['confidential'] and not here.is_assigned()", 'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: here.assigned_to() + (state_change.kwargs['username'],)")

    tdef = wf.transitions['abandoned_confidential']
    tdef.setProperties(title="""Revert to (pending) if no supporters""",
                       new_state_id="""Pending_confidential""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: status['confidential'] and not here.assigned_to()", 'guard_permissions': 'Support collector issue'},
                       )

    tdef = wf.transitions['abandoned']
    tdef.setProperties(title="""Revert to pending if no supporters""",
                       new_state_id="""Pending""",
                       trigger_type=0,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: not status['confidential'] and not here.assigned_to()", 'guard_permissions': 'Support collector issue'},
                       )

    tdef = wf.transitions['resolve']
    tdef.setProperties(title="""""",
                       new_state_id="""Resolved""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""resolve""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['reject-test']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""reject-test""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    tdef = wf.transitions['unrestrict_pending']
    tdef.setProperties(title="""""",
                       new_state_id="""Pending""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""unrestrict_pending""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    tdef = wf.transitions['request']
    tdef.setProperties(title="""""",
                       new_state_id="""""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""Request""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: not (status.has_key('requested') and status['requested'])"},
                       )
    tdef.addVariable(id='requested', text='python: 1')
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees']) ")

    tdef = wf.transitions['assign']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""assign""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'not: status/confidential', 'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    tdef = wf.transitions['accept_confidential']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""accept_confidential""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': "python: status['confidential'] and not here.is_assigned()", 'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: here.assigned_to() + (state_change.kwargs['username'],)")

    tdef = wf.transitions['assign_confidential']
    tdef.setProperties(title="""""",
                       new_state_id="""Accepted_confidential""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""None""",
                       actbox_name="""assign_confidential""",
                       actbox_url="""""",
                       actbox_category="""issue_workflow""",
                       props={'guard_expr': 'status/confidential', 'guard_permissions': 'Support collector issue'},
                       )
    tdef.addVariable(id='assigned_to', text="python: tuple(state_change.kwargs['assignees'])")

    ## State Variable
    wf.variables.setStateVar('state')

    ## Variables initialization
    vdef = wf.variables['requested']
    vdef.setProperties(description="""initial request has been done""",
                       default_value="""""",
                       default_expr="""""",
                       for_catalog=1,
                       for_status=1,
                       update_always=0,
                       props=None)

    vdef = wf.variables['confidential']
    vdef.setProperties(description="""Retain security_related issues loss of confidentiality on completion""",
                       default_value="""""",
                       default_expr="""""",
                       for_catalog=1,
                       for_status=1,
                       update_always=0,
                       props=None)

    vdef = wf.variables['assigned_to']
    vdef.setProperties(description="""Supporters assigned to the issue""",
                       default_value="""""",
                       default_expr="""""",
                       for_catalog=1,
                       for_status=1,
                       update_always=0,
                       props=None)

    ## Worklists Initialization

def createCollector_issue_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupCollector_issue_workflow(ob)
    return ob

addWorkflowFactory(createCollector_issue_workflow,
                   id='collector_issue_workflow',
                   title='Collector issue workflow')

