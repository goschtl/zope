from zope.app.folder.interfaces import IFolder

import grok

import mars.layer
import mars.view
import mars.template

from mars.formdemo.layer import IDemoDivBrowserLayer

mars.layer.layer(IDemoDivBrowserLayer)

class Index(mars.view.LayoutView):
    grok.name('index')
    grok.context(IFolder)

class IndexTemplate(mars.template.LayoutFactory):
    grok.context(Index)
    grok.template('index.pt') 
    
