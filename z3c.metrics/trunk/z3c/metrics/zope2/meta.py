from z3c.metrics import meta
from z3c.metrics.zope2 import index, ofs

class InitMetric(meta.InitMetric):

    metric_factory = ofs.InitMetric
    remove_interface = index.IRemoveScoreEvent

class SelfMetric(meta.SelfMetric):

    metric_factory = ofs.SelfMetric
    add_interface = index.IAddSelfValueEvent
    remove_interface = index.IRemoveScoreEvent

class OtherMetric(meta.OtherMetric):

    metric_factory = ofs.OtherMetric
