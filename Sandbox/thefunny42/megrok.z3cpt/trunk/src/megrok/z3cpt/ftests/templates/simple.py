"""
  >>> from megrok.z3cpt.ftests.templates.simple import *
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
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

import grok
from megrok import z3cpt

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
<p tal:content="view/description">Description</p>
</body>
</html>
""")
