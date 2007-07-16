"""
  >>> import grok
  >>> grok.grok('mars.macro.ftests.macro')

  >>> from mars.macro.ftests.macro import Mammoth
  >>> mammoth = getRootFolder()["mammoth"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> #browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> browser.open('http://localhost/mammoth/@@first')
  >>> print browser.contents
  <html>
    <body>
      <h1>First Page</h1>
      <div class="navi">
  <BLANKLINE>
  <BLANKLINE>
     <div>My Navigation</div>
  <BLANKLINE>
  <BLANKLINE>
      </div>
      <div class="content">
        Content here
      </div>
    </body>
  </html>
  <BLANKLINE>

"""

import zope.component
import zope.interface

from z3c.template.interfaces import ILayoutTemplate

import grok
import mars.macro
import mars.template

class Mammoth(grok.Model):
    pass

class Navigation(mars.macro.MacroFactory):
    """Name defaults to factory.__name__, 'navigation' and context defaults to
    module context - in this case Mammoth."""
    grok.template('templates/navigation.pt') # required

class First(grok.View):

    def __call__(self):
        template = zope.component.getMultiAdapter(
            (self, self.request), ILayoutTemplate)
        return template(self)

    def render(self):
        pass

class FirstLayout(mars.template.LayoutFactory):
    grok.template('templates/first.pt')
    grok.context(First)

