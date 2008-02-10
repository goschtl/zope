from jquery.layer import IJQueryJavaScriptBrowserLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import mars.form

class IWebSiteLayer(mars.form.IDivFormLayer, IJQueryJavaScriptBrowserLayer):
    pass

class ISeleniumTestLayer(mars.form.IDivFormLayer, IJQueryJavaScriptBrowserLayer):
    """This layer is used to set up selenium tests, usually run through
    testbrowser in selenium.txt"""
    pass
