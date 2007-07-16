"""
Testing the PageletView, which unlike grok.View will look up a layout.

  >>> import grok
  >>> grok.grok('mars.view.ftests.pagelet')
  >>> from mars.view.ftests.pagelet import Mammoth
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

These tests make use of minimal layer

  >>> skinURL = 'http://localhost/++skin++myskin'

Pagelet will use two templates, one rendered and returned from ``render`` method
and the second - a layout template - on ``__call__`` method.

  >>> browser.open(skinURL + "/manfred/@@full")
  >>> print browser.contents
  <html>
  <body><div>View template</div>
  </body>
  </html>

"""
import zope.interface

import grok
import mars.view
import mars.template
import mars.layer

class IMyLayer(mars.layer.IMinimalLayer):
    pass

# set layer on module level, all class declarations that use directive
# mars.layer.layer will use this layer - Skin, views and templates
mars.layer.layer(IMyLayer)

class MySkin(mars.layer.Skin):
    pass

class Mammoth(grok.Model):
    pass

class Full(mars.view.PageletView):
    pass

class FullLayout(mars.template.LayoutFactory):
    grok.template('templates/layout.pt')
    grok.context(Full)

class FullTemplate(mars.template.TemplateFactory):
    grok.template('templates/template.pt')
    grok.context(Full)

