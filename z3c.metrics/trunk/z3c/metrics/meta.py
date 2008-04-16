from zope import interface
from zope.configuration import fields, config
from zope.app.component import metaconfigure

from z3c.metrics import interfaces, metric, subscription

default = object()

class IMetric(interfaces.IMetric):
    """Defines what values are to be collected for an object."""

    for_ = fields.Tokens(
        title=u'Interfaces of the objects the metric applied to',
        required=True, value_type=fields.GlobalObject())

class IAttributeMetric(IMetric, interfaces.IAttributeMetric):
    """Retrieves the metric value from an interface field."""

class Metric(config.GroupingContextDecorator):

    add_interface = interfaces.IAddValueEvent
    remove_interface = interfaces.IRemoveValueEvent

    def __init__(self, context, for_, **kw):
        super(Metric, self).__init__(context, **kw)
        self.metric = self.metric_factory(**kw)
        self.object_interface = for_.pop(0)
        self.for_ = for_

    def before(self):
        object_iface = self.handler_adapts[0]
        other_ifaces = self.handler_adapts[1:]
        metaconfigure.subscriber(
            _context=self.context,
            for_=[object_iface, self.add_interface]+other_ifaces,
            handler=getattr(self.metric, self.add_handler))
        metaconfigure.subscriber(
            _context=self.context,
            for_=[object_iface, self.remove_interface]+other_ifaces,
            handler=getattr(self.metric, self.remove_handler))

    @property
    def handler_adapts(self):
        return [self.object_interface]+self.for_

class InitMetric(Metric):

    metric_factory = metric.InitMetric
    add_interface = interfaces.IInitScoreEvent
    add_handler = 'initSelfScore'
    remove_handler = 'removeSelfScore'

class SelfMetric(Metric):

    metric_factory = metric.SelfMetric
    add_handler = 'initSelfScore'
    remove_handler = 'removeSelfScore'

class OtherMetric(Metric):

    metric_factory = metric.OtherMetric
    add_handler = 'addOtherValue'
    remove_handler = 'removeOtherValue'

    @property
    def handler_adapts(self):
        return self.for_+[self.object_interface]

def weighted(_context, utility_interface, weight=default):
    sub = subscription.UtilityWeightedSubscription(
        utility_interface=utility_interface)
    if weight is not default:
        sub.weight = weight

    provides, = interface.implementedBy(sub.getChangeScoreEngine)
    metaconfigure.subscriber(
        _context=_context, provides=provides,
        for_=[interfaces.IMetric, _context.object_interface,
              interfaces.IChangeScoreEvent]+_context.for_,
        factory=sub.getChangeScoreEngine)
    provides, = interface.implementedBy(sub.getBuildScoreEngine)
    metaconfigure.subscriber(
        _context=_context, provides=provides,
        for_=[interfaces.IMetric, _context.object_interface,
              interfaces.IIndexesScoreEvent]+_context.for_,
        factory=sub.getBuildScoreEngine)
    
    
