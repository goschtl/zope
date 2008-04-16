from zope import interface, component

import Acquisition
from OFS import interfaces as ofs_ifaces

from z3c.metrics import interfaces, metric, dispatch

@component.adapter(ofs_ifaces.IItem)
@interface.implementer(dispatch.IAncestors)
def getAncestors(contained):
    ancestor = contained
    while ancestor is not None:
        yield ancestor
        ancestor = Acquisition.aq_parent(
            Acquisition.aq_inner(ancestor))

class InitMetric(metric.InitMetric):

    @component.adapter(interface.Interface,
                       interfaces.IRemoveValueEvent)
    def removeSelfScore(self, obj, event):
        if not ofs_ifaces.IObjectWillBeAddedEvent.providedBy(event):
            super(InitMetric, self).removeSelfScore(obj, event)

class SelfMetric(InitMetric, metric.SelfMetric):
    pass

class OtherMetric(metric.OtherMetric):

    @component.adapter(interface.Interface,
                       interfaces.IRemoveValueEvent,
                       interface.Interface)
    def removeOtherValue(self, other, event, obj):
        if not ofs_ifaces.IObjectWillBeAddedEvent.providedBy(event):
            super(OtherMetric, self).removeOtherValue(
                other, event, obj)

