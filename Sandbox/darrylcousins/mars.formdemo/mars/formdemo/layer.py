__docformat__ = "reStructuredText"
import grok

import mars.form

class IDemoBrowserLayer(grok.IGrokLayer):
    pass

class IDemoDivBrowserLayer(mars.form.IDivFormLayer, IDemoBrowserLayer):
    pass

class IDemoTableBrowserLayer(mars.form.ITableFormLayer, IDemoBrowserLayer):
    pass

