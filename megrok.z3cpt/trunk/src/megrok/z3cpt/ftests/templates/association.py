"""
  >>> from megrok.z3cpt.ftests.templates.association import *
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@painting")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello Paul!</h1>
  </body>
  </html>
  >>> browser.open("http://localhost/manfred/@@drawing")
  >>> print browser.contents
  <html>
  <body>
  <h1>I am a regular drawing!</h1>
  </body>
  </html>
  >>> browser.open("http://localhost/manfred/@@sketch")
  >>> print browser.contents
  <html>
  <body>
  <h1>I am a rapidly executed freehand drawing!</h1>
  </body>
  </html>

"""

import grok
from megrok import z3cpt

class Mammoth(grok.Model):
    pass


class Painting(grok.View):

    def name(self):
        return u"Paul"


class Drawing(grok.View):

    def kind(self):
        return u'regular drawing'

drawing = z3cpt.PageTemplateFile("drawing.zpt")


class Sketch(grok.View):

    def kind(self):
        return u'rapidly executed freehand drawing'

sketch = z3cpt.PageTemplate(filename="drawing.zpt")
