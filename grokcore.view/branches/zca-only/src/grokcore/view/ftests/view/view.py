"""
  >>> root = getRootFolder()
  >>> application = getApplication()
  >>> root["manfred"] = Mammoth()

  >>> from infrae.testbrowser.browser import Browser

  >>> browser = Browser(application)
  >>> browser.options.handle_errors = False

  >>> status = browser.open("http://localhost/manfred/@@painting")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello, world!</h1>
  </body>
  </html>

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class Painting(grok.View):
    pass

painting = grok.PageTemplate("""\
<html>
<body>
<h1>Hello, world!</h1>
</body>
</html>
""")
