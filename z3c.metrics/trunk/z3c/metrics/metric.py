from zope import interface, component

from z3c.metrics import interfaces

class InitMetric(object):
    interface.implements(interfaces.IMetric)

    @component.adapter(interface.Interface,
                       interfaces.IInitScoreEvent)
    def initSelfScore(self, obj, event):
        for engine in component.subscribers(
            [self, obj, event], interfaces.IEngine):
            engine.initScore()

    @component.adapter(interface.Interface,
                       interfaces.IRemoveValueEvent)
    def removeSelfScore(self, obj, event):
        for engine in component.subscribers(
            [self, obj, event], interfaces.IEngine):
            engine.removeScore()

class AttributeMetric(object):
    interface.implements(interfaces.IAttributeMetric)

    default_interface = None
    default_field_name = None

    def __init__(self, interface=None, field_name=None,
                 field_callable=False):

        if interface is None and self.default_interface is None:
            raise ValueError("Must pass an interface")
        if interface is None:
            self.interface = self.default_interface
        else:
            self.interface = interface

        if field_name is None and self.default_field_name is None:
            raise ValueError("Must pass a field_name")
        if field_name is None:
            self.field_name = self.default_field_name
        else:
            self.field_name = field_name
        self.field_callable = field_callable

    def getValueFor(self, obj):
        obj = self.interface(obj)
        value = getattr(obj, self.field_name)
        if self.field_callable:
            value = value()
        return value

class SelfMetric(InitMetric, AttributeMetric):

    @component.adapter(interface.Interface,
                       interfaces.IAddValueEvent)
    def initSelfScore(self, obj, event):
        value = self.getValueFor(obj)
        init = interfaces.IInitScoreEvent.providedBy(event)
        for engine in component.subscribers(
            [self, obj, event], interfaces.IEngine):
            if init:
                engine.initScore()
            engine.addValue(value)

class OtherMetric(AttributeMetric):

    @component.adapter(interface.Interface,
                       interfaces.IAddValueEvent,
                       interface.Interface)
    def addOtherValue(self, other, event, obj):
        value = self.getValueFor(other)
        for engine in component.subscribers(
            [self, obj, event, other], interfaces.IEngine):
            engine.addValue(value)

    @component.adapter(interface.Interface,
                       interfaces.IRemoveValueEvent,
                       interface.Interface)
    def removeOtherValue(self, other, event, obj):
        value = self.getValueFor(other)
        for engine in component.subscribers(
            [self, obj, event, other], interfaces.IEngine):
            engine.removeValue(value)
