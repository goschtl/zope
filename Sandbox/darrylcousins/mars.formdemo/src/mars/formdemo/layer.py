__docformat__ = "reStructuredText"
import mars.layer

class IDemoBrowserLayer(mars.layer.ILayer):
    pass

class IDemoDivBrowserLayer(mars.layer.IDivFormLayer, IDemoBrowserLayer):
    pass

class IDemoTableBrowserLayer(mars.layer.ITableFormLayer, IDemoBrowserLayer):
    pass

