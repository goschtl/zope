__docformat__ = "reStructuredText"
import mars.form
import mars.layer

class IDemoBrowserLayer(mars.layer.ILayer):
    pass

class IDemoDivBrowserLayer(mars.form.IDivFormLayer, IDemoBrowserLayer):
    pass

class IDemoTableBrowserLayer(mars.form.ITableFormLayer, IDemoBrowserLayer):
    pass

