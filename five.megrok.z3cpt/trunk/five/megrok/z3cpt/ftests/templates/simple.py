"""
  >>> from five.megrok.z3cpt.ftests.templates.simple import *
  >>> id = getRootFolder()._setObject("manfred", Mammoth(id='manfred'))

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@painting")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello World</h1>
  </body>
  </html>
  >>> browser.open("http://localhost/manfred/@@drawing")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello World</h1>
  <p>Nothing for the moment</p>
  </body>
  </html>

"""

from five import grok
from five.megrok import z3cpt

class Mammoth(grok.Model):
    pass


class Painting(grok.View):
    pass

painting = z3cpt.PageTemplate("""
<html>
<body>
<h1>Hello World</h1>
</body>
</html>
""")

class Drawing(grok.View):

    @property
    def description(self):
        return u'Nothing for the moment'

drawing = z3cpt.PageTemplate("""
<html>
<body>
<h1>Hello World</h1>
<p tal:content="view.description">Description</p>
</body>
</html>
""")
