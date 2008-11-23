"""
  >>> from megrok.z3cpt.ftests.templates.namespace import *
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@painting")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello Henri</h1>
  </body>
  </html>
  >>> browser.open("http://localhost/manfred/@@drawing")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello Jean</h1>
  </body>
  </html>

"""

import grok
from megrok import z3cpt

class Mammoth(grok.Model):
    pass


class Painting(grok.View):

    grok.template('namespace')

    def default_namespace(self):
        return dict(name=u'Henri')


class Drawing(grok.View):

    grok.template('namespace')

    def namespace(self):
        return dict(name='Jean')

