"""
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/++skin++Simple/manfred/@@cavedrawings")
  >>> print browser.contents
  <html>
  <body>
  <h1>Hello, world!</h1>
  </body>
  </html>

  >>> browser.open("http://localhost/++skin++Grokkerdam/manfred/@@moredrawings")
  >>> print browser.contents
  Pretty

  >>> browser.open("http://localhost/++skin++myskin/manfred/@@evenmoredrawings")
  >>> print browser.contents
  Awesome

"""
import grokcore.view as grok


class SimpleLayer(grok.IBrowserRequest):
    grok.skin('Simple')


class GrokkerdamLayer(SimpleLayer):
    grok.skin('Grokkerdam')


grok.layer(SimpleLayer)


class MySkinLayer(grok.IBrowserRequest):
    pass

class MySkin(MySkinLayer):
    grok.skin('myskin')

class Mammoth(grok.Context):
    pass

class CaveDrawings(grok.View):
    pass

cavedrawings = grok.PageTemplate("""\
<html>
<body>
<h1>Hello, world!</h1>
</body>
</html>
""")

class MoreDrawings(grok.View):
    grok.layer(GrokkerdamLayer)

    def render(self):
        return "Pretty"


class EvenMoreDrawings(grok.View):
    grok.layer(MySkinLayer)

    def render(self):
        return "Awesome"
