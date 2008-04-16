from zope import interface, component

from z3c.metrics import interfaces

class Engine(object):
    interface.implements(interfaces.IEngine)
    component.adapts(interfaces.IMetric,
                     interfaces.ISubscription,
                     interface.Interface)

    def __init__(self, metric, subscription, context):
        self.metric = metric
        self.subscription = subscription
        self.index = subscription.getIndex(context)
        self.scale = self.index.scale
        self.context = context

    def initScore(self):
        self.index.initScoreFor(self.context)

    def removeScore(self):
        self.index.removeScoreFor(self.context)

class WeightedEngine(Engine):
    component.adapts(interfaces.IMetric,
                     interfaces.IWeightedSubscription,
                     interface.Interface)
        
    def addValue(self, value):
        scaled = self.scale.fromValue(value)
        weighted = self.subscription.weight*scaled
        self.index.changeScoreFor(self.context, weighted)
        
    def changeValue(self, previous, current):
        scaled = (self.scale.fromValue(current) -
                  self.scale.fromValue(previous))
        weighted = self.subscription.weight*scaled
        self.index.changeScoreFor(self.context, weighted)
        
    def removeValue(self, value):
        scaled = self.scale.fromValue(value)
        weighted = self.subscription.weight*scaled
        self.index.changeScoreFor(self.context, -weighted)
