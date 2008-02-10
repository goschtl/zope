"""

  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> skinURL = 'http://localhost/++skin++myskin'
  >>> browser.open(skinURL + "/manfred/@@index")
  >>> print browser.contents
  <html>
  <body>
  <div id="leftcolumn">
  <div>First viewlet content</div>
  <div>Second viewlet content</div>
  <BLANKLINE>
  </div>
  <div id="rightcolumn">
  Right column content
  </div>
  </body>
  </html>

"""
import grok
import mars.layer
import mars.viewlet
import mars.view
import mars.template

### This the context of the views
### we don't need to define grok.context on the views because this is the 
### implied `module` level context
class Mammoth(grok.Model):
    title = u'Manfred'

### define a layer that will be used for all views in this module
class IModuleLayer(mars.layer.IMinimalLayer):
    pass

### all objects in module are registered to this layer
grok.layer(IModuleLayer)

### this skin uses the defined layer
class MySkin(grok.Skin):
    pass

### the page that we are looking at
class Index(mars.view.LayoutView):
    pass

### the template for index page
class IndexLayout(mars.template.LayoutFactory):
    grok.template('index.pt') # required
    grok.context(Index) # required

### a manager registered for Mammoth and IModuleLayer
class RightColumn(mars.viewlet.ViewletManager):

    def render(self):
        return u'Right column content'

### a second manager registered for Mammoth and IModuleLayer
class LeftColumn(mars.viewlet.ViewletManager):
    """Joins output of viewlets"""
    pass

### viewlets for leftcolumn manager
### vanilla viewlet with render method
class FirstViewlet(mars.viewlet.Viewlet):
    """A simple viewlet"""
    mars.viewlet.manager(LeftColumn)
    mars.viewlet.view(Index) # not required
    weight = 0

    def render(self):
        return u'<div>First viewlet content</div>'

### the second of which uses a regsitered template
class SecondViewlet(mars.viewlet.Viewlet):
    """A viewlet that has its own template"""
    mars.viewlet.manager(LeftColumn)
    weight = 1

class SecondViewletTemplate(mars.template.TemplateFactory):
    grok.template('viewlet.pt')
    grok.context(SecondViewlet)

