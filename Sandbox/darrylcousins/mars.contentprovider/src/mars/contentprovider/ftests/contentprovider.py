"""
  >>> import grok
  >>> grok.grok('mars.contentprovider.ftests.contentprovider')
  >>> from mars.contentprovider.ftests.contentprovider import Mammoth
  >>> getRootFolder()["mammoth"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> skinURL = 'http://localhost/++skin++myskin'
  >>> browser.open(skinURL + '/mammoth/@@index')
  >>> print browser.contents
  <div>
  <p>I am Manfred the Mammoth</p>
  <p>A friendly mammoth</p>
  <p>Most like a mammoth, but some don't.</p>
  </div>


"""

import grok
import mars.view
import mars.layer
import mars.template
import mars.contentprovider

class IMySkinLayer(mars.layer.IMinimalLayer):
    pass

# layer used for all registrations in this module
mars.layer.layer(IMySkinLayer)

class MySkin(mars.layer.Skin):
    pass

class Mammoth(grok.Model):
    """This is the assumed context for the module"""
    title = u'Manfred'

class Index(mars.view.LayoutView):
    pass

class IndexLayout(mars.template.LayoutFactory):
    grok.template('index.pt')
    grok.context(Index)

class Title(mars.contentprovider.ContentProvider):
    """Title uses the render method"""

    def render(self):
        return self.context.title

class Description(mars.contentprovider.ContentProvider):
    """Description will use the following template"""
    pass

class DescriptionTemplate(mars.template.TemplateFactory):
    grok.template('description.pt')
    grok.context(Description)

class Comment(mars.contentprovider.ContentProvider):
    """Comment will call update before render"""
    comment = u''

    def update(self):
       self.comment = u"Most like a mammoth, but some don't."

    def render(self):
        self.update()
        return self.comment
