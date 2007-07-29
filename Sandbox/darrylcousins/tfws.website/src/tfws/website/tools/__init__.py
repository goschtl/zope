import zope.interface

import grok

import mars.viewlet
import mars.layer

from tfws.website.layer import IWebSiteLayer

mars.layer.layer(IWebSiteLayer)

class ITools(mars.viewlet.ViewletManager):
    """Tools viewletmanager"""
    grok.name('ITools')
    grok.context(zope.interface.Interface)

