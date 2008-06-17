from datetime import datetime

import grok
from grokstar.entry import Entry
from hurry.workflow import workflow, interfaces
from hurry.workflow.interfaces import IWorkflow
from hurry.query.query import Query
from hurry.query import Eq

from grokstar.interfaces import CREATED, PUBLISHED

def publish_action(info, context):
    context.published = datetime.now()
    
def create_workflow():
    create_transition = workflow.Transition(
        transition_id='create',
        title='create',
        source=None,
        destination=CREATED)

    publish_transition = workflow.Transition(
        transition_id='publish',
        title='publish',
        source=CREATED,
        destination=PUBLISHED,
        action=publish_action)

    update_transition = workflow.Transition(
        transition_id='update',
        title='update',
        source=PUBLISHED,
        destination=PUBLISHED,
        action=publish_action)
    
    retract_transition = workflow.Transition(
        transition_id='retract',
        title='retract',
        source=PUBLISHED,
        destination=CREATED)
    
    return [create_transition, publish_transition, update_transition,
            retract_transition]

class Workflow(grok.GlobalUtility, workflow.Workflow):
    grok.provides(IWorkflow)
    
    def __init__(self):
        super(Workflow, self).__init__(create_workflow())

class Versions(grok.GlobalUtility, workflow.WorkflowVersions):

    def getVersions(self, state, id):
        q = Query()
        return q.searchResults(
            Eq(('entry_catalog', 'workflow_state'),
               state) &
            Eq(('entry_catalog', 'workflow_id'),
               id))     
    
    def getVersionsWithAutomaticTransitions(self):
        return []

    def hasVersion(self, id, state):
        return bool(len(self.getVersions(state, id)))
          
    def hasVersionId(self, id):
        q = Query()
        result = q.searchResults(
            Eq(('entry_catalog', 'workflow_id'), id))
        return bool(len(result))
    
class WorkflowState(grok.Adapter, workflow.WorkflowState):
    grok.context(Entry)
    grok.provides(interfaces.IWorkflowState)
    
class WorkflowInfo(grok.Adapter, workflow.WorkflowInfo):
    grok.context(Entry)
    grok.provides(interfaces.IWorkflowInfo)

