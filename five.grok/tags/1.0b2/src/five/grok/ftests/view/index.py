"""
  >>> from five.grok.ftests.view.index import *
  >>> id = getRootFolder()._setObject("manfred", Mammoth(id='manfred'))

The default view name for a model is 'index':

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello, world!</h1>
  <span>Blue</span>
  <span>Blue</span>
  </body>
  </html>

"""
from five import grok

class Mammoth(grok.Model):
    teeth = u"Blue"

class Index(grok.View):
    pass

index = grok.PageTemplate("""\
<html>
<body>
<h1>Hello, world!</h1>
<span tal:content="python:context.teeth">green</span>
<span tal:content="context/teeth">green</span>
</body>
</html>
""")
