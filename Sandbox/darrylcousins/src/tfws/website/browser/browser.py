from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IRootFolder

import grok

import mars.layer
import mars.view
import mars.template

from tfws.website.layer import IWebsiteLayer

mars.layer.layer(IWebsiteLayer)

grok.define_permission('tfws.ManageSites')

class Index(mars.view.PageletView):
    grok.context(IRootFolder)
    grok.require('tfws.ManageSites')

    @property
    def sites(self):
        for site in self.context:
            print site

    @property
    def addurl(self):
        url = absoluteURL(self.context, self.request)
        return url + '/add'


class IndexTemplate(mars.template.TemplateFactory):
    """layout template for `home`"""
    grok.context(Index)
    grok.template('index.pt') 
    

