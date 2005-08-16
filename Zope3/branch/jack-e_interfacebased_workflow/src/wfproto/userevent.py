from zope.interface import implements
from zope.app import zapi
from zope.app.event.objectevent import ObjectEvent

from interfaces import IUserEvent
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.stateful.interfaces import IStatefulPIAdapter


class UserEvent(ObjectEvent):

    implements(IUserEvent)

    def __init__(self, object, method, formData):
        super(UserEvent, self).__init__(object)
        self.method   = method
        self.formData = formData




def UserEventSubscriber(event):
    # XXX for now we use __processdefiniton_name__
    pd_name = getattr(event.object, '__processdefinition_name__', '')
    pia = zapi.queryAdapter(event.object, IStatefulPIAdapter, pd_name)
    if pia is not None:
        #try:
        pia.fireTransition(event.method, event)
        #except Exception, e:
        #    print 'invalid Transition', event.method, str(e)
            
