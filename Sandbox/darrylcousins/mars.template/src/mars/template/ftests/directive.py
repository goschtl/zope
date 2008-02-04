"""
Run through and test the available directives to template factories.

  >>> import grok
  >>> from mars.template.ftests.directive import Mammoth
  >>> grok.grok('mars.template.ftests.directive')

  >>> mammoth = getRootFolder()["mammoth"] = Mammoth()

Layout views have a call method (TemplateViews do not necessarily) so we will
use testbrowser.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open("http://localhost/++skin++myskin/mammoth/@@view")
  >>> print browser.contents
  <body>
  <div>Rendered content</div>
  </body>

"""
# TODO add layer directive, when you have a view grokker to use


import zope.component
import zope.interface

from z3c.template.interfaces import ILayoutTemplate

import grok
from grok.interfaces import IGrokView

import mars.template
import mars.layer
import mars.view

class IMyLayer(mars.layer.IMinimalLayer):
    pass

class MySkin(grok.Skin):
    grok.layer(IMyLayer)

class IMyPageTemplate(zope.interface.Interface):
    pass

class Mammoth(grok.Model):
    pass

class View(mars.view.LayoutView):
    """Here use LayoutView which uses layers"""
    grok.layer(IMyLayer)
    mars.view.layout('complex') # forces named layout template lookup
    _layout_interface = IMyPageTemplate # if template provides specific interface

    def render(self):
        return u'Rendered content'

class ViewLayout(mars.template.LayoutFactory):
    grok.template('templates/complex.pt') # required
    grok.context(View) # define the adapted view
    grok.name('complex') # view must use named adapter lookup
    grok.provides(IMyPageTemplate) # view must use this interface to lookup
    mars.template.macro('body') # define the macro to use
    mars.template.content_type('text/html') # define the contentType
    grok.layer(IMyLayer) # registered on this layer.
    

