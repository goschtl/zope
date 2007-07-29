from jquery.layer import IJQueryJavaScriptBrowserLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import mars.form

class IWebSiteLayer(mars.form.IDivFormLayer, IJQueryJavaScriptBrowserLayer):
#class IWebSiteLayer(IDefaultBrowserLayer, mars.form.IDivFormLayer, IJQueryJavaScriptBrowserLayer):
    pass
