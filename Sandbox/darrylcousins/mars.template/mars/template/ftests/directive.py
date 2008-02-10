"""
Run through and test the available directives to template factories.

  >>> mammoth = getRootFolder()["mammoth"] = Mammoth()

Layout views have a call method (TemplateViews do not necessarily) so we will
use testbrowser.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open("http://localhost/++skin++dirskin/mammoth/@@mammothview")
  >>> print browser.contents
  <body>
  <div>Rendered content</div>
  </body>

"""

import zope.component
import zope.interface

from z3c.template.interfaces import ILayoutTemplate

import grok
from grok.interfaces import IGrokView

import mars.template
import mars.layer
import mars.view

class DirLayer(mars.layer.IMinimalLayer):
    pass

class DirSkin(grok.Skin):
    grok.layer(DirLayer)

class IMyPageTemplate(zope.interface.Interface):
    pass

class Mammoth(grok.Model):
    pass

class MammothView(mars.view.LayoutView):
    """Here use LayoutView which uses layers"""
    grok.layer(DirLayer)
    mars.view.layout('complex') # forces named layout template lookup
    _layout_interface = IMyPageTemplate # if template provides specific interface

    def render(self):
        return u'Rendered content'

class ViewLayout(mars.template.LayoutFactory):
    grok.template('templates/complex.pt') # required
    grok.context(MammothView) # define the adapted view
    grok.name('complex') # view must use named adapter lookup
    grok.provides(IMyPageTemplate) # view must use this interface to lookup
    mars.template.macro('body') # define the macro to use
    mars.template.content_type('text/html') # define the contentType
    grok.layer(DirLayer) # registered on this layer.
    

