from zope import interface, component
from zope.schema import fieldproperty
import persistent

from z3c.metrics import interfaces, engine

default = object()

class Subscription(object):

    @component.adapter(interfaces.IMetric,
                       interface.Interface,
                       interfaces.IChangeScoreEvent) 
    @interface.implementer(interfaces.IEngine)
    def getChangeScoreEngine(self, metric, context, event, *args):
        return self.engine_factory(metric, self, context)

    @component.adapter(interfaces.IMetric,
                       interface.Interface,
                       interfaces.IIndexesScoreEvent) 
    @interface.implementer(interfaces.IEngine)
    def getBuildScoreEngine(self, metric, context, event, *args):
        if self.getIndex(context) in event.indexes:
            return self.engine_factory(metric, self, context)

class WeightedSubscription(Subscription):
    interface.implements(interfaces.IWeightedSubscription)

    engine_factory = engine.WeightedEngine

    weight = fieldproperty.FieldProperty(
        interfaces.IWeightedSubscription['weight'])

class ILocalSubscription(interfaces.ISubscription):
    """The subscribed index is stored on an attribute."""

    index = interface.Attribute('Index')

class LocalSubscription(persistent.Persistent):
    interface.implements(ILocalSubscription)
    component.adapts(interfaces.IIndex)

    def __init__(self, index):
        self.index = index

    def getIndex(self, context=None):
        return self.index

class UtilitySubscription(object):
    interface.implements(interfaces.IUtilitySubscription,
                         interfaces.ISubscription)

    utility_interface = fieldproperty.FieldProperty(
        interfaces.IUtilitySubscription['utility_interface'])

    def __init__(self, utility_interface=default):
        if utility_interface is not default:
            self.utility_interface = utility_interface

    def getIndex(self, context=None):
        return component.getUtility(
            self.utility_interface, context=context)

class UtilityWeightedSubscription(WeightedSubscription,
                                  UtilitySubscription):
    pass

class LocalWeightedSubscription(WeightedSubscription,
                                LocalSubscription):
    pass
