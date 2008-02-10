"""
Testing the LayoutView, which unlike grok.View will look up a layout.

  >>> mammoth = getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

These tests make use of minimal layer

  >>> skinURL = 'http://localhost/++skin++layoutskin'

Since a layout template is not yet registered, calling the view will fail:

  >>> browser.open(skinURL + "/manfred/@@drawing")
  Traceback (most recent call last):
  ...
  ComponentLookupError: ......

We'll manually register a layout template.

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> layout = os.path.join(temp_dir, 'layout.pt')
  >>> open(layout, 'w').write('''
  ...   <div tal:content="view/render">
  ...     Full layout
  ...   </div>
  ... ''')

  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> from z3c.template.template import TemplateFactory
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> from mars.view.ftests.layout import Drawing
  >>> factory = TemplateFactory(layout, 'text/html')
  >>> import zope.component
  >>> zope.component.provideAdapter(factory,
  ...     (Drawing, IBrowserRequest), ILayoutTemplate)

  >>> browser.open(skinURL + "/manfred/@@drawing")
  >>> print browser.contents
  <div>Rendered content</div>

  >>> import shutil
  >>> shutil.rmtree(temp_dir)

We can also use mars.template to provide the layout template.

  >>> browser.open(skinURL + "/manfred/@@view")
  >>> print browser.contents
  <div>View template</div>

"""
import grok
import mars.view
import mars.template
import mars.layer

class LayoutLayer(mars.layer.IMinimalLayer):
    pass

# set layer on module level, all class declarations that may use directive
# grok.layer will use this layer - Skin, views and templates
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
grok.layer(LayoutLayer)

class LayoutSkin(grok.Skin):
    pass

class Mammoth(grok.Model):
    pass

class Drawing(mars.view.LayoutView):
#class Drawing(grok.View):

    def render(self):
        return u'Rendered content'

class View(mars.view.LayoutView):
    pass

class ViewLayout(mars.template.LayoutFactory):
    grok.template('templates/template.pt')
    grok.context(View)

